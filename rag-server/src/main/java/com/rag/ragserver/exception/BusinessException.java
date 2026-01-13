package com.rag.ragserver.exception;

import lombok.Getter;

/**
 * 自定义业务异常，用于主动抛出业务逻辑错误
 */
@Getter
public class BusinessException extends RuntimeException {
    private final Integer code;

    public BusinessException(String message) {
        super(message);
        this.code = 400; // 默认业务错误码
    }

    public BusinessException(Integer code, String message) {
        super(message);
        this.code = code;
    }
}
