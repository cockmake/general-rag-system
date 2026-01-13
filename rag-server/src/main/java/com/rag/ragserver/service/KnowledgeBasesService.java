package com.rag.ragserver.service;

import com.rag.ragserver.domain.KnowledgeBases;
import com.baomidou.mybatisplus.extension.service.IService;

import java.util.List;
import java.util.Map;

/**
* @author make
* @description 针对表【knowledge_bases(知识库主表)】的数据库操作Service
* @createDate 2025-12-31 02:01:56
*/
public interface KnowledgeBasesService extends IService<KnowledgeBases> {
    Map<String, List<KnowledgeBases>> listByWorkspaceAndUser(Long workspaceId, Long userId);
    
    /**
     * 创建知识库，同时在 Milvus 中创建对应的数据库和集合
     */
    KnowledgeBases createKnowledgeBase(KnowledgeBases kb);
}
