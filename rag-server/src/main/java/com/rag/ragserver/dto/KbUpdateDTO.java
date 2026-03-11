package com.rag.ragserver.dto;

import com.rag.ragserver.domain.kb.KbVisibilityEnum;
import lombok.Data;

@Data
public class KbUpdateDTO {
    private String name;
    private String description;
    private String systemPrompt;
    private KbVisibilityEnum visibility;
}
