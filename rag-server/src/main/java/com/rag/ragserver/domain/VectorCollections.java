package com.rag.ragserver.domain;

import com.baomidou.mybatisplus.annotation.*;

import java.util.Date;
import lombok.Data;

/**
 * Milvus 向量集合与知识库映射表
 * @TableName vector_collections
 */
@TableName(value ="vector_collections")
@Data
public class VectorCollections {
    /**
     * 向量集合 ID
     */
    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 所属知识库 ID
     */
    private Long kbId;

    /**
     * 使用的 embedding 模型名称（如 text-embedding-3-large）
     */
    private String embeddingModel;

    /**
     * Milvus 中的 collection 名称
     */
    private String collectionName;

    /**
     * 向量维度
     */
    private Integer dim;

    /**
     * 向量距离度量方式（COSINE / L2 / IP）
     */
    private String metricType;

    /**
     * 集合状态：active 当前使用，deprecated 已废弃
     */
    private Object status;

    /**
     * 创建时间
     */
    private Date createdAt;

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
        VectorCollections other = (VectorCollections) that;
        return (this.getId() == null ? other.getId() == null : this.getId().equals(other.getId()))
            && (this.getKbId() == null ? other.getKbId() == null : this.getKbId().equals(other.getKbId()))
            && (this.getEmbeddingModel() == null ? other.getEmbeddingModel() == null : this.getEmbeddingModel().equals(other.getEmbeddingModel()))
            && (this.getCollectionName() == null ? other.getCollectionName() == null : this.getCollectionName().equals(other.getCollectionName()))
            && (this.getDim() == null ? other.getDim() == null : this.getDim().equals(other.getDim()))
            && (this.getMetricType() == null ? other.getMetricType() == null : this.getMetricType().equals(other.getMetricType()))
            && (this.getStatus() == null ? other.getStatus() == null : this.getStatus().equals(other.getStatus()))
            && (this.getCreatedAt() == null ? other.getCreatedAt() == null : this.getCreatedAt().equals(other.getCreatedAt()))
            && (this.getIsDeleted() == null ? other.getIsDeleted() == null : this.getIsDeleted().equals(other.getIsDeleted()));
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((getId() == null) ? 0 : getId().hashCode());
        result = prime * result + ((getKbId() == null) ? 0 : getKbId().hashCode());
        result = prime * result + ((getEmbeddingModel() == null) ? 0 : getEmbeddingModel().hashCode());
        result = prime * result + ((getCollectionName() == null) ? 0 : getCollectionName().hashCode());
        result = prime * result + ((getDim() == null) ? 0 : getDim().hashCode());
        result = prime * result + ((getMetricType() == null) ? 0 : getMetricType().hashCode());
        result = prime * result + ((getStatus() == null) ? 0 : getStatus().hashCode());
        result = prime * result + ((getCreatedAt() == null) ? 0 : getCreatedAt().hashCode());
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
        sb.append(", embeddingModel=").append(embeddingModel);
        sb.append(", collectionName=").append(collectionName);
        sb.append(", dim=").append(dim);
        sb.append(", metricType=").append(metricType);
        sb.append(", status=").append(status);
        sb.append(", createdAt=").append(createdAt);
        sb.append(", isDeleted=").append(isDeleted);
        sb.append("]");
        return sb.toString();
    }
}