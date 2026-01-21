package com.rag.ragserver.mapper;

import com.rag.ragserver.domain.QuerySessions;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.rag.ragserver.dto.MessageSearchResultDTO;
import org.apache.ibatis.annotations.Param;
import java.util.List;


/**
* @author make
* @description 针对表【query_sessions(RAG 查询会话上下文表)】的数据库操作Mapper
* @createDate 2026-01-02 22:22:17
* @Entity com.rag.ragserver.domain.QuerySessions
*/
public interface QuerySessionsMapper extends BaseMapper<QuerySessions> {

    List<MessageSearchResultDTO> searchMessages(
        @Param("userId") Long userId, 
        @Param("workspaceId") Long workspaceId, 
        @Param("keyword") String keyword, 
        @Param("limit") int limit, 
        @Param("offset") int offset
    );

}




