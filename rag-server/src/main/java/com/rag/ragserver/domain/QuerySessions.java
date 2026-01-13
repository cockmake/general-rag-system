package com.rag.ragserver.domain;

import com.baomidou.mybatisplus.annotation.*;

import java.util.Date;
import lombok.Data;

/**
 * RAG 查询会话上下文表
 * @TableName query_sessions
 */
@TableName(value ="query_sessions")
@Data
public class QuerySessions {
    /**
     * 会话 ID
     */
    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 用户 ID
     */
    private Long userId;

    /**
     * 前端/客户端会话标识
     */
    private String sessionKey;

    /**
     * 最后一次活跃时间
     */
    private Date lastActiveAt;

    /**
     * 创建时间
     */
    private Date createdAt;

    /**
     * 工作空间 ID
     */
    private Long workspaceId;

    /**
     * 
     */
    @TableLogic
    private Integer isDeleted;

    @Override
    public boolean equals(Object that) {
        if (this == that) {
            return true;
        }
        if (that == null) {
            return false;
        }
        if (getClass() != that.getClass()) {
            return false;
        }
        QuerySessions other = (QuerySessions) that;
        return (this.getId() == null ? other.getId() == null : this.getId().equals(other.getId()))
            && (this.getUserId() == null ? other.getUserId() == null : this.getUserId().equals(other.getUserId()))
            && (this.getSessionKey() == null ? other.getSessionKey() == null : this.getSessionKey().equals(other.getSessionKey()))
            && (this.getLastActiveAt() == null ? other.getLastActiveAt() == null : this.getLastActiveAt().equals(other.getLastActiveAt()))
            && (this.getCreatedAt() == null ? other.getCreatedAt() == null : this.getCreatedAt().equals(other.getCreatedAt()))
            && (this.getWorkspaceId() == null ? other.getWorkspaceId() == null : this.getWorkspaceId().equals(other.getWorkspaceId()))
            && (this.getIsDeleted() == null ? other.getIsDeleted() == null : this.getIsDeleted().equals(other.getIsDeleted()));
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((getId() == null) ? 0 : getId().hashCode());
        result = prime * result + ((getUserId() == null) ? 0 : getUserId().hashCode());
        result = prime * result + ((getSessionKey() == null) ? 0 : getSessionKey().hashCode());
        result = prime * result + ((getLastActiveAt() == null) ? 0 : getLastActiveAt().hashCode());
        result = prime * result + ((getCreatedAt() == null) ? 0 : getCreatedAt().hashCode());
        result = prime * result + ((getWorkspaceId() == null) ? 0 : getWorkspaceId().hashCode());
        result = prime * result + ((getIsDeleted() == null) ? 0 : getIsDeleted().hashCode());
        return result;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(getClass().getSimpleName());
        sb.append(" [");
        sb.append("Hash = ").append(hashCode());
        sb.append(", id=").append(id);
        sb.append(", userId=").append(userId);
        sb.append(", sessionKey=").append(sessionKey);
        sb.append(", lastActiveAt=").append(lastActiveAt);
        sb.append(", createdAt=").append(createdAt);
        sb.append(", workspaceId=").append(workspaceId);
        sb.append(", isDeleted=").append(isDeleted);
        sb.append("]");
        return sb.toString();
    }
}