package com.rag.ragserver.controller;

import com.rag.ragserver.common.R;
import com.rag.ragserver.domain.Notifications;
import com.rag.ragserver.service.NotificationsService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/notifications")
@RequiredArgsConstructor
public class NotificationsController {

    private final NotificationsService notificationsService;

    @GetMapping("/latest")
    public R<Notifications> getLatest() {
        return R.success(notificationsService.getLatestNotification());
    }
}
