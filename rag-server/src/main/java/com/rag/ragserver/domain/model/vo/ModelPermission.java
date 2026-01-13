package com.rag.ragserver.domain.model.vo;

import lombok.Data;

@Data
public class ModelPermission {
    private Long id;
    private String name;
    private String provider;
    private Object metadata;
    private Integer maxContextTokens;
    private Integer qpsLimit;
    private Long dailyTokenLimit;
}
