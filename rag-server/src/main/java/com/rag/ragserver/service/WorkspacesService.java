package com.rag.ragserver.service;

import com.rag.ragserver.domain.Workspaces;
import com.rag.ragserver.domain.workspace.vo.WorkspaceMemberVO;
import com.baomidou.mybatisplus.extension.service.IService;

import java.util.List;

/**
* @author make
* @description 针对表【workspaces(多租户工作空间（Workspace）表)】的数据库操作Service
* @createDate 2025-12-31 01:13:35
*/
public interface WorkspacesService extends IService<Workspaces> {
    
    /**
     * 创建工作空间
     * @param workspace 工作空间信息
     * @param userId 创建者用户ID
     * @return 创建的工作空间
     */
    Workspaces createWorkspace(Workspaces workspace, Long userId);
    
    /**
     * 邀请用户加入工作空间
     * @param workspaceId 工作空间ID
     * @param targetUserId 目标用户ID
     * @param role 角色
     * @param operatorUserId 操作者用户ID
     */
    void inviteUser(Long workspaceId, Long targetUserId, String role, Long operatorUserId);
    
    /**
     * 获取工作空间成员列表
     * @param workspaceId 工作空间ID
     * @return 成员列表
     */
    List<WorkspaceMemberVO> getWorkspaceMembers(Long workspaceId);
    
    /**
     * 移除工作空间成员
     * @param workspaceId 工作空间ID
     * @param userId 用户ID
     * @param operatorUserId 操作者用户ID
     */
    void removeMember(Long workspaceId, Long userId, Long operatorUserId);
    
    /**
     * 更新工作空间信息
     * @param workspaceId 工作空间ID
     * @param name 工作空间名称
     * @param description 工作空间描述
     * @param operatorUserId 操作者用户ID
     */
    void updateWorkspace(Long workspaceId, String name, String description, Long operatorUserId);
    
    /**
     * 切换用户当前工作空间
     * @param userId 用户ID
     * @param workspaceId 工作空间ID
     */
    void switchWorkspace(Long userId, Long workspaceId);
    
    /**
     * 验证并修复用户的当前工作空间
     * 如果当前工作空间已被删除或用户不是成员，自动切换到用户创建的第一个工作空间
     * @param userId 用户ID
     * @return 修复后的工作空间ID，如果没有可用工作空间返回null
     */
    Long validateAndFixUserWorkspace(Long userId);
}
