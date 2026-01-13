package com.rag.ragserver.domain;

import com.baomidou.mybatisplus.annotation.*;

import java.util.Date;

import lombok.Data;

/**
 * 知识库主表
 *
 * @TableName knowledge_bases
 */
@TableName(value = "knowledge_bases")
@Data
public class KnowledgeBases {
    /**
     * 知识库 ID
     */
    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 知识库名称
     */
    private String name;

    /**
     * 知识库拥有者用户 ID
     */
    private Long ownerUserId;

    /**
     * 所属工作空间 ID
     */
    private Long workspaceId;

    /**
     * 可见性：private 私有，shared 共享，public 公共
     * 如果指定 workspace_id，则 visibility 只能 shared
     * 不指定 workspace_id，则 visibility 可以是 private 或 public
     */
    private Object visibility;

    /**
     * 知识库描述
     */
    private String description;

    /**
     * 系统提示词
     */
    private String systemPrompt;

    /**
     * 扩展元数据（如 embedding 模型、语言等）
     */
    private Object metadata;

    /**
     * 创建时间
     */
    private Date createdAt;

    /**
     * 更新时间
     */
    private Date updatedAt;

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
        KnowledgeBases other = (KnowledgeBases) that;
        return (this.getId() == null ? other.getId() == null : this.getId().equals(other.getId()))
                && (this.getName() == null ? other.getName() == null : this.getName().equals(other.getName()))
                && (this.getOwnerUserId() == null ? other.getOwnerUserId() == null : this.getOwnerUserId().equals(other.getOwnerUserId()))
                && (this.getWorkspaceId() == null ? other.getWorkspaceId() == null : this.getWorkspaceId().equals(other.getWorkspaceId()))
                && (this.getVisibility() == null ? other.getVisibility() == null : this.getVisibility().equals(other.getVisibility()))
                && (this.getDescription() == null ? other.getDescription() == null : this.getDescription().equals(other.getDescription()))
                && (this.getSystemPrompt() == null ? other.getSystemPrompt() == null : this.getSystemPrompt().equals(other.getSystemPrompt()))
                && (this.getMetadata() == null ? other.getMetadata() == null : this.getMetadata().equals(other.getMetadata()))
                && (this.getCreatedAt() == null ? other.getCreatedAt() == null : this.getCreatedAt().equals(other.getCreatedAt()))
                && (this.getUpdatedAt() == null ? other.getUpdatedAt() == null : this.getUpdatedAt().equals(other.getUpdatedAt()))
                && (this.getIsDeleted() == null ? other.getIsDeleted() == null : this.getIsDeleted().equals(other.getIsDeleted()));
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((getId() == null) ? 0 : getId().hashCode());
        result = prime * result + ((getName() == null) ? 0 : getName().hashCode());
        result = prime * result + ((getOwnerUserId() == null) ? 0 : getOwnerUserId().hashCode());
        result = prime * result + ((getWorkspaceId() == null) ? 0 : getWorkspaceId().hashCode());
        result = prime * result + ((getVisibility() == null) ? 0 : getVisibility().hashCode());
        result = prime * result + ((getDescription() == null) ? 0 : getDescription().hashCode());
        result = prime * result + ((getSystemPrompt() == null) ? 0 : getSystemPrompt().hashCode());
        result = prime * result + ((getMetadata() == null) ? 0 : getMetadata().hashCode());
        result = prime * result + ((getCreatedAt() == null) ? 0 : getCreatedAt().hashCode());
        result = prime * result + ((getUpdatedAt() == null) ? 0 : getUpdatedAt().hashCode());
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
        sb.append(", name=").append(name);
        sb.append(", ownerUserId=").append(ownerUserId);
        sb.append(", workspaceId=").append(workspaceId);
        sb.append(", visibility=").append(visibility);
        sb.append(", description=").append(description);
        sb.append(", systemPrompt=").append(systemPrompt);
        sb.append(", metadata=").append(metadata);
        sb.append(", createdAt=").append(createdAt);
        sb.append(", updatedAt=").append(updatedAt);
        sb.append(", isDeleted=").append(isDeleted);
        sb.append("]");
        return sb.toString();
    }
}