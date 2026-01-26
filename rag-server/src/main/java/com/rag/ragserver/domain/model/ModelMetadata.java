package com.rag.ragserver.domain.model;

import lombok.Data;
import java.util.List;
import java.util.Map;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import java.util.HashMap;

@Data
public class ModelMetadata {
    private List<String> tools;

    // 处理其他可能的动态字段 (xxx: xxx)
    private Map<String, Object> otherProperties = new HashMap<>();

    @JsonAnySetter
    public void add(String key, Object value) {
        otherProperties.put(key, value);
    }

    @JsonAnyGetter
    public Map<String, Object> getOtherProperties() {
        return otherProperties;
    }
}
