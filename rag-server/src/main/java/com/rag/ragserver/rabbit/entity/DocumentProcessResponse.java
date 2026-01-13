package com.rag.ragserver.rabbit.entity;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.util.List;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DocumentProcessResponse implements Serializable {
    private Long documentId;
    private String status;
    private String message;
    private Integer chunksCount;
    private List<DocumentChunkDTO> chunks;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class DocumentChunkDTO implements Serializable {
        private Integer chunkIndex;
        private String text;
        private Integer tokenLength;
        private String vectorId;
        private Map<String, Object> metadata;
    }
}
