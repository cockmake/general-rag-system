package com.rag.ragserver.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.extension.handlers.JacksonTypeHandler;
import com.rag.ragserver.domain.model.ModelMetadata;
import java.util.Date;
import lombok.Data;

/**
 * 可用大模型定义表
 * @TableName models
 */
@TableName(value ="models", autoResultMap = true)
@Data
public class Models {
    /**
     * 模型 ID
     */
    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 模型名称（如 gpt-4o / deepseek-r1）
     */
    private String name;

    /**
     * 模型提供方（openai / deepseek / local）
     */
    private String provider;

    /**
     * 模型最大上下文长度
     */
    private Integer maxContextTokens;

    /**
     * 模型是否启用（0 禁用，1 启用）
     */
    private Integer enabled;

    private Object metadata;

    /**
     * 创建时间
     */
    private Date createdAt;
    /**
     * 该模型是否支持知识库选择
     */
    private Integer kbSupported;

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
        Models other = (Models) that;
        return (this.getId() == null ? other.getId() == null : this.getId().equals(other.getId()))
            && (this.getName() == null ? other.getName() == null : this.getName().equals(other.getName()))
            && (this.getProvider() == null ? other.getProvider() == null : this.getProvider().equals(other.getProvider()))
            && (this.getMaxContextTokens() == null ? other.getMaxContextTokens() == null : this.getMaxContextTokens().equals(other.getMaxContextTokens()))
            && (this.getEnabled() == null ? other.getEnabled() == null : this.getEnabled().equals(other.getEnabled()))
            && (this.getMetadata() == null ? other.getMetadata() == null : this.getMetadata().equals(other.getMetadata()))
            && (this.getCreatedAt() == null ? other.getCreatedAt() == null : this.getCreatedAt().equals(other.getCreatedAt()));
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((getId() == null) ? 0 : getId().hashCode());
        result = prime * result + ((getName() == null) ? 0 : getName().hashCode());
        result = prime * result + ((getProvider() == null) ? 0 : getProvider().hashCode());
        result = prime * result + ((getMaxContextTokens() == null) ? 0 : getMaxContextTokens().hashCode());
        result = prime * result + ((getEnabled() == null) ? 0 : getEnabled().hashCode());
        result = prime * result + ((getMetadata() == null) ? 0 : getMetadata().hashCode());
        result = prime * result + ((getCreatedAt() == null) ? 0 : getCreatedAt().hashCode());
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
        sb.append(", provider=").append(provider);
        sb.append(", maxContextTokens=").append(maxContextTokens);
        sb.append(", enabled=").append(enabled);
        sb.append(", metadata=").append(metadata);
        sb.append(", createdAt=").append(createdAt);
        sb.append("]");
        return sb.toString();
    }
}