package com.rag.ragserver.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Size;

@Data
public class WorkspaceCreateDTO {
    @NotBlank(message = "工作空间名称不能为空")
    @Size(max = 100, message = "工作空间名称长度不能超过100字符")
    private String name;
    
    @Size(max = 500, message = "描述长度不能超过500字符")
    private String description;
}
