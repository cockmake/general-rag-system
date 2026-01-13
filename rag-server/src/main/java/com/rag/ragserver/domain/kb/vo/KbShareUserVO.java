package com.rag.ragserver.domain.kb.vo;

import lombok.Data;

import java.util.Date;

/**
 * 知识库被邀请用户信息 VO
 */
@Data
public class KbShareUserVO {
    /**
     * 共享记录ID
     */
    private Long id;
    
    /**
     * 用户ID
     */
    private Long userId;
    
    /**
     * 用户名
     */
    private String username;
    
    /**
     * 邮箱
     */
    private String email;
    
    /**
     * 授权人用户ID
     */
    private Long grantedBy;
    
    /**
     * 授权人用户名
     */
    private String grantedByUsername;
    
    /**
     * 授权时间
     */
    private Date grantedAt;
}
