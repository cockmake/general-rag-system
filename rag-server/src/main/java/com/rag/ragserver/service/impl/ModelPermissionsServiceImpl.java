package com.rag.ragserver.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.rag.ragserver.domain.ModelPermissions;
import com.rag.ragserver.service.ModelPermissionsService;
import com.rag.ragserver.mapper.ModelPermissionsMapper;
import com.rag.ragserver.domain.model.vo.AvailableModelVO;
import com.rag.ragserver.domain.model.vo.ModelPermission;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * @author make
 * @description 针对表【model_permissions(角色-模型配额与限流配置表)】的数据库操作Service实现
 * @createDate 2025-12-31 01:13:35
 */
@Service
public class ModelPermissionsServiceImpl extends ServiceImpl<ModelPermissionsMapper, ModelPermissions>
        implements ModelPermissionsService {

    @Override
    public List<AvailableModelVO> getAvailableModels(Long userId) {
        return this.baseMapper.selectAvailableModelsByUserId(userId);
    }

    @Override
    public ModelPermission userHasModelPermission(Integer roleId, Long modelId) {
        return this.baseMapper.selectModelPermissionByRoleIdAndModelId(roleId, modelId);
    }
}




