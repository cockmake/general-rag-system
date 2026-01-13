package com.rag.ragserver.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.util.Date;
import lombok.Data;

/**
 * 文档切分后的最小语义单元表
 * @TableName document_chunks
 */
@TableName(value ="document_chunks")
@Data
public class DocumentChunks {
    /**
     * 文档切片 ID
     */
    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 所属文档 ID
     */
    private Long documentId;

    /**
     * 所属知识库 ID（冗余字段，加速过滤）
     */
    private Long kbId;

    /**
     * 文档内切片顺序号
     */
    private Integer chunkIndex;

    /**
     * 切片后的文本内容
     */
    private String text;

    /**
     * 该切片的 token 数
     */
    private Integer tokenLength;

    /**
     * Milvus 中对应的向量 ID
     */
    private String vectorId;

    /**
     * 切片级元数据（页码、标题、来源等）
     */
    private Object metadata;

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
        DocumentChunks other = (DocumentChunks) that;
        return (this.getId() == null ? other.getId() == null : this.getId().equals(other.getId()))
            && (this.getDocumentId() == null ? other.getDocumentId() == null : this.getDocumentId().equals(other.getDocumentId()))
            && (this.getKbId() == null ? other.getKbId() == null : this.getKbId().equals(other.getKbId()))
            && (this.getChunkIndex() == null ? other.getChunkIndex() == null : this.getChunkIndex().equals(other.getChunkIndex()))
            && (this.getText() == null ? other.getText() == null : this.getText().equals(other.getText()))
            && (this.getTokenLength() == null ? other.getTokenLength() == null : this.getTokenLength().equals(other.getTokenLength()))
            && (this.getVectorId() == null ? other.getVectorId() == null : this.getVectorId().equals(other.getVectorId()))
            && (this.getMetadata() == null ? other.getMetadata() == null : this.getMetadata().equals(other.getMetadata()))
            && (this.getCreatedAt() == null ? other.getCreatedAt() == null : this.getCreatedAt().equals(other.getCreatedAt()));
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((getId() == null) ? 0 : getId().hashCode());
        result = prime * result + ((getDocumentId() == null) ? 0 : getDocumentId().hashCode());
        result = prime * result + ((getKbId() == null) ? 0 : getKbId().hashCode());
        result = prime * result + ((getChunkIndex() == null) ? 0 : getChunkIndex().hashCode());
        result = prime * result + ((getText() == null) ? 0 : getText().hashCode());
        result = prime * result + ((getTokenLength() == null) ? 0 : getTokenLength().hashCode());
        result = prime * result + ((getVectorId() == null) ? 0 : getVectorId().hashCode());
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
        sb.append(", documentId=").append(documentId);
        sb.append(", kbId=").append(kbId);
        sb.append(", chunkIndex=").append(chunkIndex);
        sb.append(", text=").append(text);
        sb.append(", tokenLength=").append(tokenLength);
        sb.append(", vectorId=").append(vectorId);
        sb.append(", metadata=").append(metadata);
        sb.append(", createdAt=").append(createdAt);
        sb.append("]");
        return sb.toString();
    }
}