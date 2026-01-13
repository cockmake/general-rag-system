package com.rag.ragserver.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.rag.ragserver.assembler.SessionAssembler;
import com.rag.ragserver.domain.QuerySessions;
import com.rag.ragserver.domain.model.vo.ModelPermission;
import com.rag.ragserver.domain.session.vo.SessionListVO;
import com.rag.ragserver.dto.SessionCursorQuery;
import com.rag.ragserver.exception.BusinessException;
import com.rag.ragserver.service.QuerySessionsService;
import com.rag.ragserver.mapper.QuerySessionsMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

/**
 * @author make
 * @description 针对表【query_sessions(RAG 查询会话上下文表)】的数据库操作Service实现
 * @createDate 2026-01-02 22:22:17
 */
@Service
@RequiredArgsConstructor
public class QuerySessionsServiceImpl extends ServiceImpl<QuerySessionsMapper, QuerySessions>
        implements QuerySessionsService {
    private final RabbitTemplate rabbitTemplate;

    @Override
    public Boolean sessionNameGenerate(Long userId, Long sessionId, String firstMessage, ModelPermission modelPermission) {
        try {
            rabbitTemplate.convertAndSend(
                    "server.interact.llm.exchange",
                    "session.name.generate.producer.key",
                    Map.of(
                            "userId", userId,
                            "sessionId", sessionId,
                            "firstMessage", firstMessage,
                            "model", modelPermission
                    ),
                    message -> {
                        // 这里可以对消息进行一些处理
                        return message;
                    }
            );
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    @Override
    public SessionListVO listByCursor(Long userId, Long workspaceId, SessionCursorQuery query) {
        LambdaQueryWrapper<QuerySessions> qw = Wrappers.lambdaQuery();
        qw.eq(QuerySessions::getUserId, userId)
                .eq(QuerySessions::getWorkspaceId, workspaceId)
                .orderByDesc(QuerySessions::getLastActiveAt)
                .orderByDesc(QuerySessions::getId)
                .last("limit " + (query.getPageSize() + 1));

        if (query.getLastActiveAt() != null) {
            qw.and(w -> w
                    .lt(QuerySessions::getLastActiveAt, query.getLastActiveAt())
                    .or()
                    .eq(QuerySessions::getLastActiveAt, query.getLastActiveAt())
                    .lt(QuerySessions::getId, query.getLastId())
            );
        }
        List<QuerySessions> list = list(qw);

        boolean hasMore = list.size() > query.getPageSize();
        if (hasMore) list.remove(list.size() - 1);

        return SessionAssembler.toVO(list, hasMore);
    }

    @Override
    public Boolean deleteSession(Long sessionId, Long userId, Long workspaceId) {
        LambdaQueryWrapper<QuerySessions> qw = Wrappers.lambdaQuery();
        qw.eq(QuerySessions::getId, sessionId)
                .eq(QuerySessions::getUserId, userId)
                .eq(QuerySessions::getWorkspaceId, workspaceId)
                .eq(QuerySessions::getIsDeleted, 0);

        QuerySessions session = getOne(qw);
        if (session == null) {
            throw new BusinessException(404, "会话不存在或无权限删除");
        }
        return removeById(sessionId);
    }
}




