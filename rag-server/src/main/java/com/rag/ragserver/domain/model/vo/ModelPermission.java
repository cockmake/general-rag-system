package com.rag.ragserver.domain.model.vo;

import com.rag.ragserver.domain.model.ModelMetadata;
import lombok.Data;

@Data
public class ModelPermission {
    private Long id;
    private String name;
    private String provider;
    private ModelMetadata metadata;
    private Integer maxContextTokens;
    private Integer qpsLimit;
    private Long dailyTokenLimit;
}
