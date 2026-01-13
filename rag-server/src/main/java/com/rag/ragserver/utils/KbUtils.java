package com.rag.ragserver.utils;

import com.rag.ragserver.service.ModelPermissionsService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class KbUtils {
    private final ModelPermissionsService modelPermissionsService;
    // 判断某个用户是否可以使用某个数据库
}
