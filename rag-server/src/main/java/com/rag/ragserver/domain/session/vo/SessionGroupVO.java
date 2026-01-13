package com.rag.ragserver.domain.session.vo;

import com.rag.ragserver.domain.session.SessionGroupType;
import lombok.Data;

import java.util.List;

@Data
public class SessionGroupVO {

    /**
     * 分组类型（TODAY / YESTERDAY / EARLIER）
     */
    private SessionGroupType group;

    /**
     * 分组下的会话
     */
    private List<SessionItemVO> items;

    public SessionGroupVO(SessionGroupType group, List<SessionItemVO> items) {
        this.group = group;
        this.items = items;
    }
}