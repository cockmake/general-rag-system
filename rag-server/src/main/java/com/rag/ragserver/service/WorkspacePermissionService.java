package com.rag.ragserver.service;

/**
 * 工作空间权限检查服务
 */
public interface WorkspacePermissionService {
    
    /**
     * 检查用户是否为工作空间成员
     * @param workspaceId 工作空间ID
     * @param userId 用户ID
     * @return true-是成员, false-不是成员
     */
    boolean isMemberOfWorkspace(Long workspaceId, Long userId);
    
    /**
     * 检查用户是否为工作空间拥有者
     * @param workspaceId 工作空间ID
     * @param userId 用户ID
     * @return true-是拥有者, false-不是拥有者
     */
    boolean isWorkspaceOwner(Long workspaceId, Long userId);
}
