package com.rag.ragserver.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.rag.ragserver.domain.Documents;
import com.rag.ragserver.domain.KbShares;
import com.rag.ragserver.domain.KnowledgeBases;
import com.rag.ragserver.service.DocumentsService;
import com.rag.ragserver.service.KbPermissionService;
import com.rag.ragserver.service.KbSharesService;
import com.rag.ragserver.service.KnowledgeBasesService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class KbPermissionServiceImpl implements KbPermissionService {
    
    private final KnowledgeBasesService knowledgeBasesService;
    private final KbSharesService kbSharesService;
    private final DocumentsService documentsService;
    
    @Override
    public boolean canReadKb(Long kbId, Long userId, Long workspaceId) {
        KnowledgeBases kb = knowledgeBasesService.getById(kbId);
        if (kb == null) {
            return false;
        }
        
        // 1. 如果是拥有者，可以访问
        if (userId.equals(kb.getOwnerUserId())) {
            return true;
        }
        
        // 2. 如果是public，所有人都可以读
        if ("public".equals(kb.getVisibility())) {
            return true;
        }
        
        // 3. 如果是shared，检查是否在同一workspace
        if ("shared".equals(kb.getVisibility()) && workspaceId != null 
            && workspaceId.equals(kb.getWorkspaceId())) {
            return true;
        }
        
        // 4. 检查是否在kb_shares中被授权
        LambdaQueryWrapper<KbShares> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(KbShares::getKbId, kbId)
               .eq(KbShares::getUserId, userId);
        long count = kbSharesService.count(wrapper);
        
        return count > 0;
    }
    
    @Override
    public boolean canWriteKb(Long kbId, Long userId, Long workspaceId) {
        KnowledgeBases kb = knowledgeBasesService.getById(kbId);
        if (kb == null) {
            return false;
        }
        
        // 只有拥有者可以写入（上传文档等）
        // 即使是shared或public的知识库，也只有拥有者可以上传文档
        return userId.equals(kb.getOwnerUserId());
    }
    
    @Override
    public boolean isKbOwner(Long kbId, Long userId) {
        KnowledgeBases kb = knowledgeBasesService.getById(kbId);
        if (kb == null) {
            return false;
        }
        return userId.equals(kb.getOwnerUserId());
    }
    
    @Override
    public boolean canModifyDocument(Long docId, Long userId) {
        Documents document = documentsService.getById(docId);
        if (document == null) {
            return false;
        }
        
        // 1. 如果是文档上传者，可以修改
        if (userId.equals(document.getUploaderId())) {
            return true;
        }
        
        // 2. 如果是知识库拥有者，也可以修改
        return isKbOwner(document.getKbId(), userId);
    }
}
