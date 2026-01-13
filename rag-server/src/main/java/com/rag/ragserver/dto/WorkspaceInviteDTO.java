package com.rag.ragserver.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;

@Data
public class WorkspaceInviteDTO {
    @NotNull(message = "工作空间ID不能为空")
    private Long workspaceId;
    
    @NotBlank(message = "用户名或邮箱不能为空")
    private String userIdentifier;
    
    // 移除 role 字段，后端固定为 member
}
