package com.rag.ragserver.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.rag.ragserver.domain.Users;
import com.rag.ragserver.service.UsersService;
import com.rag.ragserver.mapper.UsersMapper;
import org.springframework.stereotype.Service;

/**
* @author make
* @description 针对表【users(系统用户表)】的数据库操作Service实现
* @createDate 2025-12-31 01:13:35
*/
@Service
public class UsersServiceImpl extends ServiceImpl<UsersMapper, Users>
    implements UsersService{
}




