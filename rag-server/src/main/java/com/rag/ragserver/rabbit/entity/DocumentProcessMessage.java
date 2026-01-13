package com.rag.ragserver.rabbit.entity;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DocumentProcessMessage implements Serializable {
    private Long documentId;
    private Long kbId;
    private Long userId;
    private String filePath;
    private String fileName;
    private String bucketName;
}
