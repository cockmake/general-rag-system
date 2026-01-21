package com.rag.ragserver.service;

import com.rag.ragserver.domain.Notifications;
import com.baomidou.mybatisplus.extension.service.IService;

/**
* @author make
* @description 针对表【notifications(前端公告)】的数据库操作Service
* @createDate 2026-01-21 16:51:30
*/
public interface NotificationsService extends IService<Notifications> {

    Notifications getLatestNotification();
}
