package com.rag.ragserver.rabbit.entity;

import lombok.Data;

@Data
public class SessionNameGenerateResponse {
    private Long sessionId;
    private Long userId;
    private String sessionKey;
}
