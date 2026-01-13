package com.rag.ragserver.dto;

import lombok.Data;

import javax.validation.constraints.NotNull;
import java.util.Map;

@Data
public class ChatStart {
    @NotNull(message = "请选择模型")
    private Long modelId;
    private Long kbId;
    private String question;
    // 可扩展内容
    private Map<String, Object> options;
}
