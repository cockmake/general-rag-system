package com.rag.ragserver.dto;

import com.rag.ragserver.domain.kb.KbVisibilityEnum;
import lombok.Data;
import org.hibernate.validator.constraints.Length;

import javax.validation.constraints.NotNull;

@Data
public class KbCreateDTO {
    @NotNull(message = "知识库名称不能为空")
    @Length(max = 100, message = "知识库名称不能超过100个字符")
    private String name;
    @Length(max = 200, message = "知识库描述不能超过200个字符")
    private String description;
    private KbVisibilityEnum visibility;
}
