package com.rag.ragserver.utils;

import com.rag.ragserver.service.ModelPermissionsService;
import com.rag.ragserver.domain.model.vo.ModelPermission;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class ModelUtils {
    private final ModelPermissionsService modelPermissionsService;
    // 判断当前用户是否可用某个模型
    public ModelPermission canUseModel(Integer roleId, Long modelId) {
        return modelPermissionsService.userHasModelPermission(roleId, modelId);
    }
    // 判断当前用户是否可以用某个知识库
}
