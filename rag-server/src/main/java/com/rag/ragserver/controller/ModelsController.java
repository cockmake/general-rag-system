package com.rag.ragserver.controller;

import com.rag.ragserver.common.R;
import com.rag.ragserver.service.ModelPermissionsService;
import com.rag.ragserver.domain.model.vo.AvailableModelVO;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.servlet.http.HttpServletRequest;
import java.util.List;

@RestController
@RequestMapping("/models")
@RequiredArgsConstructor
public class ModelsController {
    private final ModelPermissionsService modelPermissionsService;
    private final HttpServletRequest request;
    @GetMapping("/available")
    public R<List<AvailableModelVO>> availableModels(){
        Long userId = (Long) request.getAttribute("userId");
        List<AvailableModelVO> availableModels = modelPermissionsService.getAvailableModels(userId);
        return R.success(availableModels);
    }
}
