package com.rag.ragserver.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.rag.ragserver.domain.Models;
import com.rag.ragserver.service.ModelsService;
import com.rag.ragserver.mapper.ModelsMapper;
import org.springframework.stereotype.Service;

/**
* @author make
* @description 针对表【models(可用大模型定义表)】的数据库操作Service实现
* @createDate 2026-01-02 15:21:42
*/
@Service
public class ModelsServiceImpl extends ServiceImpl<ModelsMapper, Models>
    implements ModelsService{

}




