package com.rag.ragserver.service;

import com.rag.ragserver.domain.ModelPermissions;
import com.baomidou.mybatisplus.extension.service.IService;
import com.rag.ragserver.domain.model.vo.AvailableModelVO;
import com.rag.ragserver.domain.model.vo.ModelPermission;

import java.util.List;

/**
* @author make
* @description 针对表【model_permissions(角色-模型配额与限流配置表)】的数据库操作Service
* @createDate 2025-12-31 01:13:35
*/
public interface ModelPermissionsService extends IService<ModelPermissions> {
    List<AvailableModelVO> getAvailableModels(Long userId);
    ModelPermission userHasModelPermission(Integer roleId, Long modelId);
}
