package com.rag.ragserver.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.rag.ragserver.domain.Users;
import com.rag.ragserver.domain.WorkspaceMembers;
import com.rag.ragserver.domain.Workspaces;
import com.rag.ragserver.domain.workspace.vo.WorkspaceMemberVO;
import com.rag.ragserver.exception.BusinessException;
import com.rag.ragserver.mapper.WorkspaceMembersMapper;
import com.rag.ragserver.mapper.WorkspacesMapper;
import com.rag.ragserver.service.UsersService;
import com.rag.ragserver.service.WorkspacePermissionService;
import com.rag.ragserver.service.WorkspacesService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Date;
import java.util.List;

/**
 * @author make
 * @description 针对表【workspaces(多租户工作空间（Workspace）表)】的数据库操作Service实现
 * @createDate 2025-12-31 01:13:35
 */
@Service
@RequiredArgsConstructor
public class WorkspacesServiceImpl extends ServiceImpl<WorkspacesMapper, Workspaces>
        implements WorkspacesService {

    private final WorkspaceMembersMapper workspaceMembersMapper;
    private final WorkspacePermissionService workspacePermissionService;
    private final UsersService usersService;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Workspaces createWorkspace(Workspaces workspace, Long userId) {
        workspace.setOwnerUserId(userId);
        // workspace.setCreatedAt(new Date());

        if (!save(workspace)) {
            throw new BusinessException("创建工作空间失败");
        }

        WorkspaceMembers member = new WorkspaceMembers();
        member.setWorkspaceId(workspace.getId());
        member.setUserId(userId);
        member.setRole("owner");
        // member.setJoinedAt(new Date());

        if (workspaceMembersMapper.insert(member) <= 0) {
            throw new BusinessException("添加工作空间成员失败");
        }

        return workspace;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void inviteUser(Long workspaceId, Long targetUserId, String role, Long operatorUserId) {
        if (!workspacePermissionService.isWorkspaceOwner(workspaceId, operatorUserId)) {
            throw new BusinessException(403, "只有工作空间拥有者才能邀请成员");
        }

        Workspaces workspace = getById(workspaceId);
        if (workspace == null) {
            throw new BusinessException(404, "工作空间不存在");
        }

        Users targetUser = usersService.getById(targetUserId);
        if (targetUser == null) {
            throw new BusinessException(404, "目标用户不存在");
        }
        
        LambdaQueryWrapper<WorkspaceMembers> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(WorkspaceMembers::getWorkspaceId, workspaceId)
               .eq(WorkspaceMembers::getUserId, targetUserId);
        Long existingCount = workspaceMembersMapper.selectCount(wrapper);
        
        if (existingCount != null && existingCount > 0) {
            throw new BusinessException("该用户已经是工作空间成员");
        }

        WorkspaceMembers member = new WorkspaceMembers();
        member.setWorkspaceId(workspaceId);
        member.setUserId(targetUserId);
        member.setRole(role);
        // member.setJoinedAt(new Date());

        if (workspaceMembersMapper.insert(member) <= 0) {
            throw new BusinessException("邀请用户失败");
        }
    }

    @Override
    public List<WorkspaceMemberVO> getWorkspaceMembers(Long workspaceId) {
        Workspaces workspace = getById(workspaceId);
        if (workspace == null) {
            throw new BusinessException(404, "工作空间不存在");
        }

        return workspaceMembersMapper.selectMembersWithUserInfo(workspaceId);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void removeMember(Long workspaceId, Long userId, Long operatorUserId) {
        if (!workspacePermissionService.isWorkspaceOwner(workspaceId, operatorUserId)) {
            throw new BusinessException(403, "只有工作空间拥有者才能移除成员");
        }

        Workspaces workspace = getById(workspaceId);
        if (workspace == null) {
            throw new BusinessException(404, "工作空间不存在");
        }

        if (workspace.getOwnerUserId().equals(userId)) {
            throw new BusinessException("不能移除工作空间拥有者");
        }
        
        LambdaQueryWrapper<WorkspaceMembers> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(WorkspaceMembers::getWorkspaceId, workspaceId)
               .eq(WorkspaceMembers::getUserId, userId);
        int deleted = workspaceMembersMapper.delete(wrapper);
        
        if (deleted <= 0) {
            throw new BusinessException("该用户不是工作空间成员");
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void updateWorkspace(Long workspaceId, String name, String description, Long operatorUserId) {
        Workspaces workspace = getById(workspaceId);
        if (workspace == null) {
            throw new BusinessException(404, "工作空间不存在");
        }

        if (!workspace.getOwnerUserId().equals(operatorUserId)) {
            throw new BusinessException(403, "只有工作空间的原始创建者才能修改工作空间信息");
        }

        if (name != null && !name.trim().isEmpty()) {
            workspace.setName(name);
        }
        if (description != null) {
            workspace.setDescription(description);
        }

        if (!updateById(workspace)) {
            throw new BusinessException("更新工作空间失败");
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void switchWorkspace(Long userId, Long workspaceId) {
        if (!workspacePermissionService.isMemberOfWorkspace(workspaceId, userId)) {
            throw new BusinessException(403, "您不是该工作空间的成员");
        }

        Users user = usersService.getById(userId);
        if (user == null) {
            throw new BusinessException(404, "用户不存在");
        }

        user.setWorkspaceId(workspaceId);
        if (!usersService.updateById(user)) {
            throw new BusinessException("切换工作空间失败");
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Long validateAndFixUserWorkspace(Long userId) {
        Users user = usersService.getById(userId);
        if (user == null) {
            return null;
        }

        Long currentWorkspaceId = user.getWorkspaceId();
        
        if (currentWorkspaceId != null) {
            Workspaces currentWorkspace = getById(currentWorkspaceId);
            if (currentWorkspace != null && workspacePermissionService.isMemberOfWorkspace(currentWorkspaceId, userId)) {
                return currentWorkspaceId;
            }
        }

        List<Workspaces> ownedWorkspaces = lambdaQuery()
                .eq(Workspaces::getOwnerUserId, userId)
                .orderByAsc(Workspaces::getCreatedAt)
                .list();

        if (!ownedWorkspaces.isEmpty()) {
            Long newWorkspaceId = ownedWorkspaces.get(0).getId();
            user.setWorkspaceId(newWorkspaceId);
            usersService.updateById(user);
            return newWorkspaceId;
        }

        Workspaces defaultWorkspace = new Workspaces();
        defaultWorkspace.setName("Default Workspace");
        defaultWorkspace.setDescription("Default workspace for " + user.getUsername());
        defaultWorkspace.setCanEdit(0);
        createWorkspace(defaultWorkspace, userId);

        user.setWorkspaceId(defaultWorkspace.getId());
        usersService.updateById(user);
        return defaultWorkspace.getId();
    }
}



