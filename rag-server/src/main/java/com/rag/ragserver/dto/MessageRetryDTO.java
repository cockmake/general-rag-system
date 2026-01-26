package com.rag.ragserver.dto;

import lombok.Data;

import javax.validation.constraints.NotNull;

@Data
public class MessageRetryDTO {
    @NotNull(message = "会话ID不能为空")
    private Long sessionId;

    @NotNull(message = "模型ID不能为空")
    private Long modelId;

    private Long kbId;

    private java.util.Map<String, Object> options;
}
