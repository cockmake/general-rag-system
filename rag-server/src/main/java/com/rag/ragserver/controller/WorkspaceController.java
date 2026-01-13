package com.rag.ragserver.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.rag.ragserver.common.R;
import com.rag.ragserver.domain.Users;
import com.rag.ragserver.domain.WorkspaceMembers;
import com.rag.ragserver.domain.Workspaces;
import com.rag.ragserver.domain.workspace.vo.WorkspaceMemberVO;
import com.rag.ragserver.domain.workspace.vo.WorkspaceVO;
import com.rag.ragserver.dto.WorkspaceCreateDTO;
import com.rag.ragserver.dto.WorkspaceInviteDTO;
import com.rag.ragserver.dto.WorkspaceUpdateDTO;
import com.rag.ragserver.exception.BusinessException;
import com.rag.ragserver.mapper.WorkspaceMembersMapper;
import com.rag.ragserver.mapper.WorkspacesMapper;
import com.rag.ragserver.service.UsersService;
import com.rag.ragserver.service.WorkspacePermissionService;
import com.rag.ragserver.service.WorkspacesService;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.BeanUtils;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletRequest;
import javax.validation.Valid;
import java.util.*;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/workspaces")
@RequiredArgsConstructor
@Validated
public class WorkspaceController {
    private final WorkspacesService workspacesService;
    private final WorkspacesMapper workspacesMapper;
    private final WorkspaceMembersMapper workspaceMembersMapper;
    private final UsersService usersService;
    private final WorkspacePermissionService workspacePermissionService;
    private final HttpServletRequest request;

    /**
     * 获取用户的工作空间列表
     *
     * @return 工作空间列表（拥有的、加入的、当前的）
     */
    @GetMapping("/list")
    public R<Map<String, Object>> getWorkspaces() {
        Long userId = (Long) request.getAttribute("userId");
        Long currentWorkspaceId = (Long) request.getAttribute("workspaceId");

        // 1. 查询用户自己创建的工作空间（workspaces.owner_user_id = userId）
        List<Workspaces> ownedWorkspaces = workspacesService.lambdaQuery()
                .eq(Workspaces::getOwnerUserId, userId)
                .orderByDesc(Workspaces::getCreatedAt)
                .list();

        // 2. 查询用户作为成员的所有工作空间（workspace_members.user_id = userId）
        List<Long> memberWorkspaceIds = workspaceMembersMapper.selectList(
                new LambdaQueryWrapper<WorkspaceMembers>()
                        .select(WorkspaceMembers::getWorkspaceId)
                        .eq(WorkspaceMembers::getUserId, userId)
        ).stream().map(WorkspaceMembers::getWorkspaceId).collect(Collectors.toList());

        // 3. 获取作为成员的工作空间，排除自己创建的
        List<Workspaces> joinedWorkspaces = new ArrayList<>();
        if (!memberWorkspaceIds.isEmpty()) {
            Set<Long> ownedWorkspaceIds = ownedWorkspaces.stream()
                    .map(Workspaces::getId)
                    .collect(Collectors.toSet());

            List<Long> joinedWorkspaceIds = memberWorkspaceIds.stream()
                    .filter(id -> !ownedWorkspaceIds.contains(id))
                    .collect(Collectors.toList());

            if (!joinedWorkspaceIds.isEmpty()) {
                joinedWorkspaces = workspacesService.lambdaQuery()
                        .in(Workspaces::getId, joinedWorkspaceIds)
                        .orderByDesc(Workspaces::getCreatedAt)
                        .list();
            }
        }

        // 4. 转换为 VO
        List<WorkspaceVO> ownedVOs = ownedWorkspaces.stream().map(w -> {
            WorkspaceVO vo = new WorkspaceVO();
            BeanUtils.copyProperties(w, vo);
            return vo;
        }).collect(Collectors.toList());

        List<WorkspaceVO> joinedVOs = joinedWorkspaces.stream().map(w -> {
            WorkspaceVO vo = new WorkspaceVO();
            BeanUtils.copyProperties(w, vo);
            return vo;
        }).collect(Collectors.toList());

        // 5. 获取当前工作空间
        WorkspaceVO currentWorkspaceVO = null;
        if (currentWorkspaceId != null) {
            Workspaces currentWorkspace = workspacesService.getById(currentWorkspaceId);
            if (currentWorkspace != null) {
                currentWorkspaceVO = new WorkspaceVO();
                BeanUtils.copyProperties(currentWorkspace, currentWorkspaceVO);
            }
        }

        Map<String, Object> result = new HashMap<>();
        result.put("owned", ownedVOs);
        result.put("member", joinedVOs);
        result.put("current", currentWorkspaceVO);

        return R.success(result);
    }

    /**
     * 创建工作空间
     *
     * @param dto 工作空间创建信息
     * @return 创建的工作空间
     */
    @PostMapping
    public R<WorkspaceVO> createWorkspace(@Valid @RequestBody WorkspaceCreateDTO dto) {
        Long userId = (Long) request.getAttribute("userId");

        Workspaces workspace = new Workspaces();
        workspace.setName(dto.getName());
        workspace.setDescription(dto.getDescription());

        Workspaces created = workspacesService.createWorkspace(workspace, userId);

        WorkspaceVO vo = new WorkspaceVO();
        BeanUtils.copyProperties(created, vo);

        return R.success(vo);
    }

    /**
     * 更新工作空间信息
     *
     * @param workspaceId 工作空间ID
     * @param dto         更新信息
     * @return 更新结果
     */
    @PutMapping("/{workspaceId}")
    public R<Void> updateWorkspace(
            @PathVariable Long workspaceId,
            @Valid @RequestBody WorkspaceUpdateDTO dto) {
        Long userId = (Long) request.getAttribute("userId");

        Workspaces workspace = workspacesService.getById(workspaceId);
        if (workspace == null) {
            throw new BusinessException(404, "工作空间不存在");
        }

        if (!workspace.getOwnerUserId().equals(userId)) {
            throw new BusinessException(403, "只有工作空间的原始创建者才能修改工作空间信息");
        }

        workspacesService.updateWorkspace(workspaceId, dto.getName(), dto.getDescription(), userId);

        return R.success();
    }

    /**
     * 删除工作空间
     *
     * @param workspaceId 工作空间ID
     * @return 删除结果
     */
    @DeleteMapping("/{workspaceId}")
    public R<Void> deleteWorkspace(@PathVariable Long workspaceId) {
        Long userId = (Long) request.getAttribute("userId");

        Workspaces workspace = workspacesService.getById(workspaceId);
        if (workspace == null) {
            throw new BusinessException(404, "工作空间不存在");
        }

        if (!workspace.getOwnerUserId().equals(userId)) {
            throw new BusinessException(403, "只有工作空间的原始创建者才能删除工作空间");
        }
        if (workspace.getCanEdit() == 0) {
            throw new BusinessException("当前工作空间不允许被删除");
        }
        if (!workspacesService.removeById(workspaceId)) {
            throw new BusinessException("删除工作空间失败");
        }

        return R.success();
    }

    /**
     * 切换当前工作空间
     *
     * @param workspaceId 工作空间ID
     * @return 切换结果
     */
    @PostMapping("/{workspaceId}/switch")
    public R<Void> switchWorkspace(@PathVariable Long workspaceId) {
        Long userId = (Long) request.getAttribute("userId");

        workspacesService.switchWorkspace(userId, workspaceId);

        return R.success();
    }

    /**
     * 邀请用户加入工作空间
     *
     * @param dto 邀请信息
     * @return 邀请结果
     */
    @PostMapping("/invite")
    public R<Void> inviteUserToWorkspace(@Valid @RequestBody WorkspaceInviteDTO dto) {
        Long operatorUserId = (Long) request.getAttribute("userId");

        Users targetUser = usersService.lambdaQuery()
                .eq(Users::getUsername, dto.getUserIdentifier())
                .or()
                .eq(Users::getEmail, dto.getUserIdentifier())
                .one();

        if (targetUser == null) {
            throw new BusinessException(404, "目标用户不存在");
        }

        // 固定角色为 member，不允许邀请为 owner
        workspacesService.inviteUser(dto.getWorkspaceId(), targetUser.getId(), "member", operatorUserId);

        return R.success();
    }

    /**
     * 获取工作空间成员列表
     *
     * @param workspaceId 工作空间ID
     * @return 成员列表
     */
    @GetMapping("/{workspaceId}/members")
    public R<List<WorkspaceMemberVO>> getWorkspaceMembers(@PathVariable Long workspaceId) {
        Long userId = (Long) request.getAttribute("userId");

        if (!workspacePermissionService.isMemberOfWorkspace(workspaceId, userId)) {
            throw new BusinessException(403, "您不是该工作空间的成员");
        }

        List<WorkspaceMemberVO> members = workspacesService.getWorkspaceMembers(workspaceId);

        return R.success(members);
    }

    /**
     * 移除工作空间成员
     *
     * @param workspaceId 工作空间ID
     * @param userId      用户ID
     * @return 移除结果
     */
    @DeleteMapping("/{workspaceId}/members/{userId}")
    public R<Void> removeUserFromWorkspace(
            @PathVariable Long workspaceId,
            @PathVariable Long userId) {
        Long operatorUserId = (Long) request.getAttribute("userId");

        workspacesService.removeMember(workspaceId, userId, operatorUserId);

        return R.success();
    }
}
