package com.rag.ragserver.dto;

import lombok.Data;

import javax.validation.constraints.NotEmpty;

@Data
public class LoginRequest {
    @NotEmpty(message = "用户名或邮箱不能为空")
    private String username;
    @NotEmpty(message = "密码不能为空")
    private String password;
    private Boolean rememberMe;
}
