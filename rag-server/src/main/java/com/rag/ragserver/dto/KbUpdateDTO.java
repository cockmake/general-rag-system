package com.rag.ragserver.dto;

import lombok.Data;

@Data
public class KbUpdateDTO {
    private String name;
    private String description;
    private String systemPrompt;
}
