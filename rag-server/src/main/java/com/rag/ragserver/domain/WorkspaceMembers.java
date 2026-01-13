package com.rag.ragserver.domain;

import com.baomidou.mybatisplus.annotation.*;

import java.util.Date;
import lombok.Data;

/**
 * 
 * @TableName workspace_members
 */
@TableName(value ="workspace_members")
@Data
public class WorkspaceMembers {
    /**
     * 
     */
    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 
     */
    private Long workspaceId;

    /**
     * 
     */
    private Long userId;

    /**
     * owner 和 member
     */
    private String role;

    /**
     * 
     */
    private Date joinedAt;

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
        WorkspaceMembers other = (WorkspaceMembers) that;
        return (this.getId() == null ? other.getId() == null : this.getId().equals(other.getId()))
            && (this.getWorkspaceId() == null ? other.getWorkspaceId() == null : this.getWorkspaceId().equals(other.getWorkspaceId()))
            && (this.getUserId() == null ? other.getUserId() == null : this.getUserId().equals(other.getUserId()))
            && (this.getRole() == null ? other.getRole() == null : this.getRole().equals(other.getRole()))
            && (this.getJoinedAt() == null ? other.getJoinedAt() == null : this.getJoinedAt().equals(other.getJoinedAt()))
            && (this.getIsDeleted() == null ? other.getIsDeleted() == null : this.getIsDeleted().equals(other.getIsDeleted()));
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((getId() == null) ? 0 : getId().hashCode());
        result = prime * result + ((getWorkspaceId() == null) ? 0 : getWorkspaceId().hashCode());
        result = prime * result + ((getUserId() == null) ? 0 : getUserId().hashCode());
        result = prime * result + ((getRole() == null) ? 0 : getRole().hashCode());
        result = prime * result + ((getJoinedAt() == null) ? 0 : getJoinedAt().hashCode());
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
        sb.append(", workspaceId=").append(workspaceId);
        sb.append(", userId=").append(userId);
        sb.append(", role=").append(role);
        sb.append(", joinedAt=").append(joinedAt);
        sb.append(", isDeleted=").append(isDeleted);
        sb.append("]");
        return sb.toString();
    }
}