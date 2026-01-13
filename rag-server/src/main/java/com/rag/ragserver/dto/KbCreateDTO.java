package com.rag.ragserver.dto;

import com.rag.ragserver.domain.kb.KbVisibilityEnum;
import lombok.Data;

import javax.validation.constraints.NotNull;

@Data
public class KbCreateDTO {
    @NotNull(message = "知识库名称不能为空")
    private String name;
    private String description;
    private KbVisibilityEnum visibility;
}
