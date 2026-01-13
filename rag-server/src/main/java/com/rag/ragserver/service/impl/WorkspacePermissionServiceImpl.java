package com.rag.ragserver.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.rag.ragserver.domain.WorkspaceMembers;
import com.rag.ragserver.domain.Workspaces;
import com.rag.ragserver.mapper.WorkspaceMembersMapper;
import com.rag.ragserver.mapper.WorkspacesMapper;
import com.rag.ragserver.service.WorkspacePermissionService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class WorkspacePermissionServiceImpl implements WorkspacePermissionService {
    
    private final WorkspacesMapper workspacesMapper;
    private final WorkspaceMembersMapper workspaceMembersMapper;
    
    @Override
    public boolean isMemberOfWorkspace(Long workspaceId, Long userId) {
        if (workspaceId == null || userId == null) {
            return false;
        }
        
        LambdaQueryWrapper<WorkspaceMembers> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(WorkspaceMembers::getWorkspaceId, workspaceId)
               .eq(WorkspaceMembers::getUserId, userId);
        Long count = workspaceMembersMapper.selectCount(wrapper);
        
        return count != null && count > 0;
    }
    
    @Override
    public boolean isWorkspaceOwner(Long workspaceId, Long userId) {
        if (workspaceId == null || userId == null) {
            return false;
        }
        
        LambdaQueryWrapper<WorkspaceMembers> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(WorkspaceMembers::getWorkspaceId, workspaceId)
               .eq(WorkspaceMembers::getUserId, userId)
               .eq(WorkspaceMembers::getRole, "owner");
        Long count = workspaceMembersMapper.selectCount(wrapper);
        
        return count != null && count > 0;
    }
}
