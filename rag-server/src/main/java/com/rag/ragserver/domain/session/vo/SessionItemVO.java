package com.rag.ragserver.domain.session.vo;

import com.rag.ragserver.domain.QuerySessions;
import lombok.Data;

import java.time.LocalDateTime;
import java.time.ZoneId;

@Data
public class SessionItemVO {

    /**
     * 会话 ID
     */
    private Long id;

    /**
     * 会话标题（当前用 sessionKey，后续可换 AI 生成名）
     */
    private String title;

    /**
     * 最后活跃时间（前端展示用）
     */
    private LocalDateTime lastActiveAt;

    /**
     * 时间戳（用于排序 / Conversations 组件）
     */
    private Long timestamp;

    public SessionItemVO(QuerySessions session) {
        this.id = session.getId();
        this.title = session.getSessionKey(); // 后续可换 session_name
        this.lastActiveAt = LocalDateTime.ofInstant(
                session.getLastActiveAt().toInstant(),
                ZoneId.systemDefault()
        );
        this.timestamp = session.getLastActiveAt().getTime();
    }
}
