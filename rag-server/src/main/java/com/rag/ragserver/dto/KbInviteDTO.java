package com.rag.ragserver.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;

/**
 * 知识库邀请 DTO
 */
@Data
public class KbInviteDTO {
    /**
     * 知识库ID
     */
    @NotNull(message = "知识库ID不能为空")
    private Long kbId;
    
    /**
     * 用户名或邮箱
     */
    @NotBlank(message = "用户名或邮箱不能为空")
    private String userIdentifier;
}
