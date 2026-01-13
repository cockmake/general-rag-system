package com.rag.ragserver.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.rag.ragserver.common.R;
import com.rag.ragserver.domain.Documents;
import com.rag.ragserver.domain.KnowledgeBases;
import com.rag.ragserver.domain.QuerySessions;
import com.rag.ragserver.domain.Users;
import com.rag.ragserver.domain.dashboard.vo.DashboardSummaryVO;
import com.rag.ragserver.service.*;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.servlet.http.HttpServletRequest;

@RestController
@RequestMapping("/dashboard")
@RequiredArgsConstructor
public class DashboardController {

    private final UsersService usersService;
    private final KnowledgeBasesService knowledgeBasesService;
    private final DocumentsService documentsService;
    private final QuerySessionsService querySessionsService;
    private final ConversationMessagesService conversationMessagesService;
    private final HttpServletRequest request;

    @GetMapping("/summary")
    public R<DashboardSummaryVO> getSummary() {
        Long userId = (Long) request.getAttribute("userId");
        Long workspaceId = (Long) request.getAttribute("workspaceId");

        DashboardSummaryVO summary = new DashboardSummaryVO();

        LambdaQueryWrapper<Users> userWrapper = new LambdaQueryWrapper<>();
        userWrapper.eq(Users::getWorkspaceId, workspaceId);
        summary.setUserCount(usersService.count(userWrapper));

        LambdaQueryWrapper<KnowledgeBases> kbWrapper = new LambdaQueryWrapper<>();
        kbWrapper.eq(KnowledgeBases::getOwnerUserId, userId);
        summary.setKbCount(knowledgeBasesService.count(kbWrapper));

        LambdaQueryWrapper<Documents> docWrapper = new LambdaQueryWrapper<>();
        docWrapper.eq(Documents::getUploaderId, userId);
        summary.setDocumentCount(documentsService.count(docWrapper));

        LambdaQueryWrapper<QuerySessions> sessionWrapper = new LambdaQueryWrapper<>();
        sessionWrapper.eq(QuerySessions::getUserId, userId);
        summary.setSessionCount(querySessionsService.count(sessionWrapper));

        // Calculate today's token usage from conversation messages
        summary.setTodayTokenUsage(conversationMessagesService.countTodayTokens(userId));

        return R.success(summary);
    }
}
