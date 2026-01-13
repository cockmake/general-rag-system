package com.rag.ragserver.domain;

import com.baomidou.mybatisplus.annotation.*;

import java.util.Date;
import lombok.Data;

/**
 * 知识库共享与权限控制表
 * @TableName kb_shares
 */
@TableName(value ="kb_shares")
@Data
public class KbShares {
    /**
     * 共享记录 ID
     */
    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 知识库 ID
     */
    private Long kbId;

    /**
     * 被授权用户 ID
     */
    private Long userId;

    /**
     * 授权人用户 ID
     */
    private Long grantedBy;

    /**
     * 授权时间
     */
    private Date grantedAt;

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
        KbShares other = (KbShares) that;
        return (this.getId() == null ? other.getId() == null : this.getId().equals(other.getId()))
            && (this.getKbId() == null ? other.getKbId() == null : this.getKbId().equals(other.getKbId()))
            && (this.getUserId() == null ? other.getUserId() == null : this.getUserId().equals(other.getUserId()))
            && (this.getGrantedBy() == null ? other.getGrantedBy() == null : this.getGrantedBy().equals(other.getGrantedBy()))
            && (this.getGrantedAt() == null ? other.getGrantedAt() == null : this.getGrantedAt().equals(other.getGrantedAt()))
            && (this.getIsDeleted() == null ? other.getIsDeleted() == null : this.getIsDeleted().equals(other.getIsDeleted()));
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((getId() == null) ? 0 : getId().hashCode());
        result = prime * result + ((getKbId() == null) ? 0 : getKbId().hashCode());
        result = prime * result + ((getUserId() == null) ? 0 : getUserId().hashCode());
        result = prime * result + ((getGrantedBy() == null) ? 0 : getGrantedBy().hashCode());
        result = prime * result + ((getGrantedAt() == null) ? 0 : getGrantedAt().hashCode());
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
        sb.append(", kbId=").append(kbId);
        sb.append(", userId=").append(userId);
        sb.append(", grantedBy=").append(grantedBy);
        sb.append(", grantedAt=").append(grantedAt);
        sb.append(", isDeleted=").append(isDeleted);
        sb.append("]");
        return sb.toString();
    }
}