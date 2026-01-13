package com.rag.ragserver.dto;

import lombok.Data;
import lombok.EqualsAndHashCode;

import javax.validation.constraints.NotNull;
import java.util.Map;

@Data
public class ChatStream {
    @NotNull(message = "会话ID不能为空")
    private Long sessionId;
    @NotNull(message = "请选择模型")
    private Long modelId;
    private Long kbId;
    @NotNull(message = "请输入消息内容")
    private String question;
    // 可扩展内容
    private Map<String, Object> options;
}
