package com.rag.ragserver.common;

import lombok.Data;

import java.io.Serializable;

@Data
public class R<T> implements Serializable {
    private Integer code;
    private String message;
    private T data;

    public static <T> R<T> success() {
        R<T> r = new R<>();
        r.setCode(200);
        r.setMessage("操作成功");
        return r;
    }

    public static <T> R<T> success(T data) {
        R<T> r = new R<>();
        r.setCode(200);
        r.setMessage("操作成功");
        r.setData(data);
        return r;
    }

    public static <T> R<T> error(String message) {
        R<T> r = new R<>();
        r.setCode(500);
        r.setMessage(message);
        return r;
    }

    public static <T> R<T> error(Integer code, String message) {
        R<T> r = new R<>();
        r.setCode(code);
        r.setMessage(message);
        return r;
    }
}