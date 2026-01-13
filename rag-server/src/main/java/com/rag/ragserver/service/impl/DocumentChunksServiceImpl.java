package com.rag.ragserver.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.rag.ragserver.domain.DocumentChunks;
import com.rag.ragserver.service.DocumentChunksService;
import com.rag.ragserver.mapper.DocumentChunksMapper;
import org.springframework.stereotype.Service;

/**
* @author make
* @description 针对表【document_chunks(文档切分后的最小语义单元表)】的数据库操作Service实现
* @createDate 2026-01-06 06:08:07
*/
@Service
public class DocumentChunksServiceImpl extends ServiceImpl<DocumentChunksMapper, DocumentChunks>
    implements DocumentChunksService{

}




