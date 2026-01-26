package com.rag.ragserver.domain;

import com.baomidou.mybatisplus.annotation.*;

import java.util.Date;
import lombok.Data;

/**
 * RAG 对话消息历史表
 * @TableName conversation_messages
 */
@TableName(value ="conversation_messages", autoResultMap = true)
@Data
public class ConversationMessages {
    /**
     * 对话消息 ID
     */
    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 所属会话 ID，对应 query_sessions.id
     */
    private Long sessionId;

    /**
     * 用户 ID（冗余字段，便于查询与审计）
     */
    private Long userId;

    /**
     * 当前使用的知识库 ID（冗余字段）
     */
    private Long kbId;

    /**
     * 消息角色：user / assistant / system
     */
    private Object role;

    /**
     * 消息文本内容
     */
    private String content;

    /**
     * 消息的状态 'pending','generating','completed','aborted','error'
     */
    private Object status;

    /**
     * 本次生成使用的模型（assistant 消息才有）
     */
    private Long modelId;

    /**
     * prompt token 数
     */
    private Integer promptTokens;

    /**
     * completion token 数
     */
    private Integer completionTokens;

    /**
     * 总 token 数
     */
    private Integer totalTokens;

    /**
     * RAG 检索上下文信息（命中的 chunk / doc / score 等）
     */
    private Object ragContext;

    /**
     * 本次生成耗时（毫秒）
     */
    private Long latencyMs;

    /**
     * 消息创建时间
     */
    private Date createdAt;

    /**
     * 
     */
    @TableLogic
    private Integer isDeleted;

    /**
     * 
     */
    @TableField(typeHandler = com.baomidou.mybatisplus.extension.handlers.JacksonTypeHandler.class)
    private Object options;

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
        ConversationMessages other = (ConversationMessages) that;
        return (this.getId() == null ? other.getId() == null : this.getId().equals(other.getId()))
            && (this.getSessionId() == null ? other.getSessionId() == null : this.getSessionId().equals(other.getSessionId()))
            && (this.getUserId() == null ? other.getUserId() == null : this.getUserId().equals(other.getUserId()))
            && (this.getKbId() == null ? other.getKbId() == null : this.getKbId().equals(other.getKbId()))
            && (this.getRole() == null ? other.getRole() == null : this.getRole().equals(other.getRole()))
            && (this.getContent() == null ? other.getContent() == null : this.getContent().equals(other.getContent()))
            && (this.getStatus() == null ? other.getStatus() == null : this.getStatus().equals(other.getStatus()))
            && (this.getModelId() == null ? other.getModelId() == null : this.getModelId().equals(other.getModelId()))
            && (this.getPromptTokens() == null ? other.getPromptTokens() == null : this.getPromptTokens().equals(other.getPromptTokens()))
            && (this.getCompletionTokens() == null ? other.getCompletionTokens() == null : this.getCompletionTokens().equals(other.getCompletionTokens()))
            && (this.getTotalTokens() == null ? other.getTotalTokens() == null : this.getTotalTokens().equals(other.getTotalTokens()))
            && (this.getRagContext() == null ? other.getRagContext() == null : this.getRagContext().equals(other.getRagContext()))
            && (this.getLatencyMs() == null ? other.getLatencyMs() == null : this.getLatencyMs().equals(other.getLatencyMs()))
            && (this.getCreatedAt() == null ? other.getCreatedAt() == null : this.getCreatedAt().equals(other.getCreatedAt()))
            && (this.getIsDeleted() == null ? other.getIsDeleted() == null : this.getIsDeleted().equals(other.getIsDeleted()))
            && (this.getOptions() == null ? other.getOptions() == null : this.getOptions().equals(other.getOptions()));
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((getId() == null) ? 0 : getId().hashCode());
        result = prime * result + ((getSessionId() == null) ? 0 : getSessionId().hashCode());
        result = prime * result + ((getUserId() == null) ? 0 : getUserId().hashCode());
        result = prime * result + ((getKbId() == null) ? 0 : getKbId().hashCode());
        result = prime * result + ((getRole() == null) ? 0 : getRole().hashCode());
        result = prime * result + ((getContent() == null) ? 0 : getContent().hashCode());
        result = prime * result + ((getStatus() == null) ? 0 : getStatus().hashCode());
        result = prime * result + ((getModelId() == null) ? 0 : getModelId().hashCode());
        result = prime * result + ((getPromptTokens() == null) ? 0 : getPromptTokens().hashCode());
        result = prime * result + ((getCompletionTokens() == null) ? 0 : getCompletionTokens().hashCode());
        result = prime * result + ((getTotalTokens() == null) ? 0 : getTotalTokens().hashCode());
        result = prime * result + ((getRagContext() == null) ? 0 : getRagContext().hashCode());
        result = prime * result + ((getLatencyMs() == null) ? 0 : getLatencyMs().hashCode());
        result = prime * result + ((getCreatedAt() == null) ? 0 : getCreatedAt().hashCode());
        result = prime * result + ((getIsDeleted() == null) ? 0 : getIsDeleted().hashCode());
        result = prime * result + ((getOptions() == null) ? 0 : getOptions().hashCode());
        return result;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(getClass().getSimpleName());
        sb.append(" [");
        sb.append("Hash = ").append(hashCode());
        sb.append(", id=").append(id);
        sb.append(", sessionId=").append(sessionId);
        sb.append(", userId=").append(userId);
        sb.append(", kbId=").append(kbId);
        sb.append(", role=").append(role);
        sb.append(", content=").append(content);
        sb.append(", status=").append(status);
        sb.append(", modelId=").append(modelId);
        sb.append(", promptTokens=").append(promptTokens);
        sb.append(", completionTokens=").append(completionTokens);
        sb.append(", totalTokens=").append(totalTokens);
        sb.append(", ragContext=").append(ragContext);
        sb.append(", latencyMs=").append(latencyMs);
        sb.append(", createdAt=").append(createdAt);
        sb.append(", isDeleted=").append(isDeleted);
        sb.append(", options=").append(options);
        sb.append("]");
        return sb.toString();
    }
}