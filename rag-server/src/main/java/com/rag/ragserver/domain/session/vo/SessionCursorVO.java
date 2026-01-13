package com.rag.ragserver.domain.session.vo;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@AllArgsConstructor
public class SessionCursorVO {

    /**
     * 下一页游标：最后一条会话的时间
     */
    private LocalDateTime lastActiveAt;

    /**
     * 下一页游标：最后一条会话 ID
     */
    private Long lastId;
}
