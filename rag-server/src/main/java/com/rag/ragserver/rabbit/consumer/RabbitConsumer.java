package com.rag.ragserver.rabbit.consumer;


import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.rag.ragserver.domain.DocumentChunks;
import com.rag.ragserver.domain.Documents;
import com.rag.ragserver.domain.QuerySessions;
import com.rag.ragserver.rabbit.entity.DocumentProcessResponse;
import com.rag.ragserver.rabbit.entity.SessionNameGenerateResponse;
import com.rag.ragserver.service.DocumentChunksService;
import com.rag.ragserver.service.DocumentsService;
import com.rag.ragserver.service.KnowledgeBasesService;
import com.rag.ragserver.service.QuerySessionsService;
import com.rag.ragserver.utils.SessionTitleAwaitManager;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.annotation.Exchange;
import org.springframework.amqp.rabbit.annotation.Queue;
import org.springframework.amqp.rabbit.annotation.QueueBinding;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

import java.util.Date;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Slf4j
@Component
@RequiredArgsConstructor
public class RabbitConsumer {
    private final QuerySessionsService querySessionsService;
    private final DocumentsService documentsService;
    private final DocumentChunksService documentChunksService;
    private final KnowledgeBasesService knowledgeBasesService;
    private final ObjectMapper objectMapper;
    
    private final SessionTitleAwaitManager sseManager;

    @RabbitListener(bindings = @QueueBinding(
            value = @Queue(value = "session.name.generate.consumer.queue", durable = "true"),
            exchange = @Exchange(value = "server.interact.llm.exchange", type = "direct", durable = "true"),
            key = "session.name.generate.consumer.key"
    ))
    public void receiveMessage(SessionNameGenerateResponse response) {
        log.info("receive message: {}", response);
        LambdaUpdateWrapper<QuerySessions> updateWrapper = new LambdaUpdateWrapper<>();
        updateWrapper.eq(QuerySessions::getId, response.getSessionId()).set(QuerySessions::getSessionKey, response.getSessionKey());
        querySessionsService.update(updateWrapper);
        // 推送 SSE 事件
        sseManager.send(
                response.getSessionId(),
                "session_title",
                Map.of("title", response.getSessionKey())
        );
    }

    @RabbitListener(bindings = @QueueBinding(
            value = @Queue(value = "rag.document.complete.queue", durable = "true"),
            exchange = @Exchange(value = "server.interact.llm.exchange", type = "direct", durable = "true"),
            key = "rag.document.complete.key"
    ))
    public void receiveDocumentCompleteMessage(DocumentProcessResponse response) {
        log.info("Received DocumentProcessResponse: {}", response);
        if ("success".equals(response.getStatus())) {
            Documents doc = documentsService.getById(response.getDocumentId());
            if (doc != null) {
                doc.setStatus("ready");
                documentsService.updateById(doc);

                if (response.getChunks() != null && !response.getChunks().isEmpty()) {
                    LambdaQueryWrapper<DocumentChunks> queryWrapper = new LambdaQueryWrapper<>();
                    queryWrapper.eq(DocumentChunks::getDocumentId, response.getDocumentId());
                    documentChunksService.remove(queryWrapper);

                    List<DocumentChunks> chunks = response.getChunks().stream().map(dto -> {
                        DocumentChunks chunk = new DocumentChunks();
                        chunk.setDocumentId(response.getDocumentId());
                        chunk.setKbId(doc.getKbId());
                        chunk.setChunkIndex(dto.getChunkIndex());
                        chunk.setText(dto.getText());
                        chunk.setTokenLength(dto.getTokenLength());
                        chunk.setVectorId(dto.getVectorId());
                        try {
                            chunk.setMetadata(objectMapper.writeValueAsString(dto.getMetadata()));
                        } catch (Exception e) {
                            chunk.setMetadata("{}");
                        }
                        chunk.setCreatedAt(new Date());
                        return chunk;
                    }).collect(Collectors.toList());
                    documentChunksService.saveBatch(chunks);
                }
            }
        } else {
            Documents doc = documentsService.getById(response.getDocumentId());
            if (doc != null) {
                doc.setStatus("failed");
                documentsService.updateById(doc);
            }
        }
    }
}
