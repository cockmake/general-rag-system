package com.rag.ragserver.mapper;

import com.rag.ragserver.domain.Workspaces;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

/**
* @author make
* @description 针对表【workspaces(多租户工作空间（Workspace）表)】的数据库操作Mapper
* @createDate 2025-12-31 01:13:35
* @Entity com.rag.ragserver.domain.Workspaces
*/
public interface WorkspacesMapper extends BaseMapper<Workspaces> {
    List<Workspaces> selectWorkspacesByUserId(@Param("userId") Long userId);
}




