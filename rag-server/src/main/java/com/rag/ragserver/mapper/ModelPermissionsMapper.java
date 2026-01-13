package com.rag.ragserver.mapper;

import com.rag.ragserver.domain.ModelPermissions;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.rag.ragserver.domain.model.vo.AvailableModelVO;
import com.rag.ragserver.domain.model.vo.ModelPermission;
import org.apache.ibatis.annotations.Param;
import java.util.List;

/**
* @author make
* @description 针对表【model_permissions(角色-模型配额与限流配置表)】的数据库操作Mapper
* @createDate 2025-12-31 01:13:35
* @Entity com.rag.ragserver.domain.ModelPermissions
*/
public interface ModelPermissionsMapper extends BaseMapper<ModelPermissions> {
    List<AvailableModelVO> selectAvailableModelsByUserId(
            @Param("userId") Long userId
    );
    ModelPermission selectModelPermissionByRoleIdAndModelId(
            @Param("roleId") Integer roleId,
            @Param("modelId") Long modelId
    );
}




