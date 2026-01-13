package com.rag.ragserver.service;

import com.rag.ragserver.domain.ModelPermissions;
import com.rag.ragserver.domain.QuerySessions;
import com.baomidou.mybatisplus.extension.service.IService;
import com.rag.ragserver.domain.model.vo.ModelPermission;
import com.rag.ragserver.domain.session.vo.SessionListVO;
import com.rag.ragserver.dto.SessionCursorQuery;

/**
* @author make
* @description 针对表【query_sessions(RAG 查询会话上下文表)】的数据库操作Service
* @createDate 2026-01-02 22:22:17
*/
public interface QuerySessionsService extends IService<QuerySessions> {
    Boolean sessionNameGenerate(Long userId, Long sessionId, String firstMessage, ModelPermission modelPermission);
    SessionListVO listByCursor(
            Long userId,
            Long workspaceId,
            SessionCursorQuery query
    );
    Boolean deleteSession(Long sessionId, Long userId, Long workspaceId);

}
