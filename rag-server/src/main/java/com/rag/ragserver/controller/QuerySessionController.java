package com.rag.ragserver.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.rag.ragserver.common.R;
import com.rag.ragserver.domain.QuerySessions;
import com.rag.ragserver.domain.session.vo.SessionListVO;
import com.rag.ragserver.dto.SessionCursorQuery;
import com.rag.ragserver.exception.BusinessException;
import com.rag.ragserver.service.QuerySessionsService;
import com.rag.ragserver.utils.SessionTitleAwaitManager;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import javax.servlet.http.HttpServletRequest;
import java.util.Map;

@RestController
@RequestMapping("/sessions")
@RequiredArgsConstructor
public class QuerySessionController {
    private final QuerySessionsService querySessionsService;
    private final HttpServletRequest request;
    private final SessionTitleAwaitManager sseManager;

    @PostMapping("/list")
    public R<SessionListVO> listSessions(
            @RequestBody SessionCursorQuery query
    ) {
        Long userId = (Long) request.getAttribute("userId");
        Long workspaceId = (Long) request.getAttribute("workspaceId");

        return R.success(
                querySessionsService.listByCursor(userId, workspaceId, query)
        );
    }

    @DeleteMapping("/{sessionId}")
    public R<Void> deleteSession(@PathVariable Long sessionId) {

        Long userId = (Long) request.getAttribute("userId");
        Long workspaceId = (Long) request.getAttribute("workspaceId");

        Boolean f = querySessionsService.deleteSession(sessionId, userId, workspaceId);
        if (f) {
            return R.success();
        }
        throw new BusinessException(404, "会话不存在或无权限删除");
    }


    @GetMapping("/{sessionId}/title/await")
    public SseEmitter connect(@PathVariable Long sessionId) {
        Long userId = (Long) request.getAttribute("userId");
        Long workspaceId = (Long) request.getAttribute("workspaceId");
        QuerySessions session = querySessionsService.getOne(
                new LambdaQueryWrapper<QuerySessions>()
                        .eq(QuerySessions::getId, sessionId)
                        .eq(QuerySessions::getUserId, userId)
                        .eq(QuerySessions::getWorkspaceId, workspaceId)
        );
        if (session == null) {
            throw new BusinessException(404, "session 不存在");
        }
        return sseManager.connect(sessionId);
    }
}
