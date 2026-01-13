package com.rag.ragserver.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.rag.ragserver.domain.Roles;
import com.rag.ragserver.service.RolesService;
import com.rag.ragserver.mapper.RolesMapper;
import org.springframework.stereotype.Service;

/**
* @author make
* @description 针对表【roles(用户角色与等级定义表.)】的数据库操作Service实现
* @createDate 2025-12-31 01:13:35
*/
@Service
public class RolesServiceImpl extends ServiceImpl<RolesMapper, Roles>
    implements RolesService{

}




