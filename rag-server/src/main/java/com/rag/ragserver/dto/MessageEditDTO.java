package com.rag.ragserver.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;

@Data
public class MessageEditDTO {
    @NotNull(message = "会话ID不能为空")
    private Long sessionId;

    @NotNull(message = "模型ID不能为空")
    private Long modelId;

    private Long kbId;

    @NotBlank(message = "新问题内容不能为空")
    private String newContent;
}
