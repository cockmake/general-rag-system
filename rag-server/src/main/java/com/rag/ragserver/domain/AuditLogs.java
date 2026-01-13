package com.rag.ragserver.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.util.Date;
import lombok.Data;

/**
 * 系统操作审计日志表
 * @TableName audit_logs
 */
@TableName(value ="audit_logs")
@Data
public class AuditLogs {
    /**
     * 审计日志 ID
     */
    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 操作用户 ID
     */
    private Long userId;

    /**
     * 操作类型（如 CREATE_KB / QUERY / UPLOAD_DOC）
     */
    private String action;

    /**
     * 操作对象类型（KB / DOCUMENT / USER 等）
     */
    private String targetType;

    /**
     * 操作对象 ID
     */
    private Long targetId;

    /**
     * 操作详情（扩展信息）
     */
    private Object detail;

    /**
     * 操作时间
     */
    private Date createdAt;

    /**
     * 操作状态 (SUCCESS/FAIL)
     */
    private String status;

    /**
     * 错误信息
     */
    private String errorMessage;

    /**
     * 耗时(ms)
     */
    private Long duration;

    /**
     * 前端展示信息
     */
    private String displayMessage;
}