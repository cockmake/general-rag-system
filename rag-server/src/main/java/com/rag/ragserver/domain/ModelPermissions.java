package com.rag.ragserver.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.util.Date;
import lombok.Data;

/**
 * 角色-模型配额与限流配置表
 * @TableName model_permissions
 */
@TableName(value ="model_permissions")
@Data
public class ModelPermissions {
    /**
     * 权限配置 ID
     */
    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 角色 ID，对应 roles.id
     */
    private Integer roleId;

    /**
     * 模型 ID，对应 models.id
     */
    private Long modelId;

    /**
     * 单次请求最大 token 数
     */
    private Integer maxTokens;

    /**
     * 每秒最大请求数
     */
    private Integer qpsLimit;

    /**
     * 每日 token 上限（NULL 表示不限）
     */
    private Long dailyTokenLimit;

    /**
     * 创建时间
     */
    private Date createdAt;

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
        ModelPermissions other = (ModelPermissions) that;
        return (this.getId() == null ? other.getId() == null : this.getId().equals(other.getId()))
            && (this.getRoleId() == null ? other.getRoleId() == null : this.getRoleId().equals(other.getRoleId()))
            && (this.getModelId() == null ? other.getModelId() == null : this.getModelId().equals(other.getModelId()))
            && (this.getMaxTokens() == null ? other.getMaxTokens() == null : this.getMaxTokens().equals(other.getMaxTokens()))
            && (this.getQpsLimit() == null ? other.getQpsLimit() == null : this.getQpsLimit().equals(other.getQpsLimit()))
            && (this.getDailyTokenLimit() == null ? other.getDailyTokenLimit() == null : this.getDailyTokenLimit().equals(other.getDailyTokenLimit()))
            && (this.getCreatedAt() == null ? other.getCreatedAt() == null : this.getCreatedAt().equals(other.getCreatedAt()));
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((getId() == null) ? 0 : getId().hashCode());
        result = prime * result + ((getRoleId() == null) ? 0 : getRoleId().hashCode());
        result = prime * result + ((getModelId() == null) ? 0 : getModelId().hashCode());
        result = prime * result + ((getMaxTokens() == null) ? 0 : getMaxTokens().hashCode());
        result = prime * result + ((getQpsLimit() == null) ? 0 : getQpsLimit().hashCode());
        result = prime * result + ((getDailyTokenLimit() == null) ? 0 : getDailyTokenLimit().hashCode());
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
        sb.append(", roleId=").append(roleId);
        sb.append(", modelId=").append(modelId);
        sb.append(", maxTokens=").append(maxTokens);
        sb.append(", qpsLimit=").append(qpsLimit);
        sb.append(", dailyTokenLimit=").append(dailyTokenLimit);
        sb.append(", createdAt=").append(createdAt);
        sb.append("]");
        return sb.toString();
    }
}