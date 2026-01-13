package com.rag.ragserver.mapper;

import com.rag.ragserver.domain.WorkspaceMembers;
import com.rag.ragserver.domain.workspace.vo.WorkspaceMemberVO;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

/**
* @author make
* @description 针对表【workspace_members】的数据库操作Mapper
* @createDate 2025-12-31 04:32:12
* @Entity com.rag.ragserver.domain.WorkspaceMembers
*/
public interface WorkspaceMembersMapper extends BaseMapper<WorkspaceMembers> {
    
    /**
     * 查询工作空间成员列表（包含用户信息）
     * @param workspaceId 工作空间ID
     * @return 成员列表
     */
    List<WorkspaceMemberVO> selectMembersWithUserInfo(@Param("workspaceId") Long workspaceId);
}




