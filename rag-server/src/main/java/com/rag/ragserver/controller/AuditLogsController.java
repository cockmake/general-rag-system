package com.rag.ragserver.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.rag.ragserver.common.R;
import com.rag.ragserver.domain.AuditLogs;
import com.rag.ragserver.service.AuditLogsService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import javax.servlet.http.HttpServletRequest;
import java.util.Arrays;
import java.util.List;

@RestController
@RequestMapping("/audit-logs")
@RequiredArgsConstructor
public class AuditLogsController {

    private final AuditLogsService auditLogsService;
    private final HttpServletRequest request;

    /**
     * 获取最近的活动日志（用于 Dashboard）
     * 只返回重要的业务操作类型
     */
    @GetMapping("/recent")
    public R<List<AuditLogs>> getRecentActivity(@RequestParam(defaultValue = "10") Integer limit) {
        Long userId = (Long) request.getAttribute("userId");
        
        // 定义感兴趣的操作类型
        List<String> importantActions = Arrays.asList(
            "createKnowledgeBase",   // 创建知识库
            "deleteKnowledgeBase",   // 删除知识库
            "uploadDocuments",       // 上传文档
            "deleteDocument",        // 删除文档
            "renameDocument",        // 重命名文档
            "inviteUserToKb",        // 邀请成员至知识库
            "createWorkspace",       // 创建工作空间
            "inviteUserToWorkspace", // 邀请成员至工作空间
            "switchWorkspace"        // 切换工作空间
        );

        Page<AuditLogs> page = new Page<>(1, limit);
        LambdaQueryWrapper<AuditLogs> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(AuditLogs::getUserId, userId)
               .in(AuditLogs::getAction, importantActions)
               .orderByDesc(AuditLogs::getCreatedAt);

        Page<AuditLogs> result = auditLogsService.page(page, wrapper);
        return R.success(result.getRecords());
    }
}
