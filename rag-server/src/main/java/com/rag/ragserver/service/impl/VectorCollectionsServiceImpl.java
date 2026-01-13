package com.rag.ragserver.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.rag.ragserver.domain.VectorCollections;
import com.rag.ragserver.service.VectorCollectionsService;
import com.rag.ragserver.mapper.VectorCollectionsMapper;
import org.springframework.stereotype.Service;

/**
* @author make
* @description 针对表【vector_collections(Milvus 向量集合与知识库映射表)】的数据库操作Service实现
* @createDate 2025-12-31 01:13:35
*/
@Service
public class VectorCollectionsServiceImpl extends ServiceImpl<VectorCollectionsMapper, VectorCollections>
    implements VectorCollectionsService{

}




