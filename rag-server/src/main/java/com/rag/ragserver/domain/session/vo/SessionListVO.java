package com.rag.ragserver.domain.session.vo;

import lombok.Data;

import java.util.List;

@Data
public class SessionListVO {

    /**
     * 按时间分组后的会话列表
     */
    private List<SessionGroupVO> groups;

    /**
     * 是否还有更多
     */
    private Boolean hasMore;

    /**
     * 下一页游标
     */
    private SessionCursorVO nextCursor;

    public SessionListVO(
            List<SessionGroupVO> groups,
            Boolean hasMore,
            SessionCursorVO nextCursor
    ) {
        this.groups = groups;
        this.hasMore = hasMore;
        this.nextCursor = nextCursor;
    }
}
