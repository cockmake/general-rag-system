package com.rag.ragserver.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.rag.ragserver.domain.Notifications;
import com.rag.ragserver.service.NotificationsService;
import com.rag.ragserver.mapper.NotificationsMapper;
import org.springframework.stereotype.Service;

/**
 * @author make
 * @description 针对表【notifications(前端公告)】的数据库操作Service实现
 * @createDate 2026-01-21 16:51:30
 */
@Service
public class NotificationsServiceImpl extends ServiceImpl<NotificationsMapper, Notifications>
        implements NotificationsService {

    @Override
    public Notifications getLatestNotification() {
        return this.lambdaQuery()
                .orderByDesc(Notifications::getCreatedAt)
                .last("limit 1")
                .one();
    }
}




