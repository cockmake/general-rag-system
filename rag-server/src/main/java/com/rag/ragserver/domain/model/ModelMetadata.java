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
}
