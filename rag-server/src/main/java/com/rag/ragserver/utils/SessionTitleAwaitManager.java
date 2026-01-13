package com.rag.ragserver.utils;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Slf4j
@Component
public class SessionTitleAwaitManager {

    private final Map<Long, SseEmitter> emitters = new ConcurrentHashMap<>();

    public SseEmitter connect(Long sessionId) {
        SseEmitter emitter = new SseEmitter(0L); // 不超时，直到完成
        emitters.put(sessionId, emitter);

        emitter.onCompletion(() -> emitters.remove(sessionId));
        emitter.onTimeout(() -> emitters.remove(sessionId));
        emitter.onError(e -> emitters.remove(sessionId));

        return emitter;
    }

    public void send(Long sessionId, String event, Object data) {
        SseEmitter emitter = emitters.get(sessionId);
        if (emitter == null) return;
        try {
            emitter.send(
                    SseEmitter.event()
                            .name(event)
                            .data(data)
            );
        } catch (Exception e) {
            // 客户端主动断开连接是正常现象，无需打印堆栈
            emitters.remove(sessionId);
        } finally {
            emitter.complete();
        }
    }
}

