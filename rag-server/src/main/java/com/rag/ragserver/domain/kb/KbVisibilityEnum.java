package com.rag.ragserver.domain.kb;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;
import lombok.Data;
import lombok.Getter;
import lombok.Setter;

@Getter
public enum KbVisibilityEnum {
    PRIVATE("private"),
    SHARED("shared"),
    PUBLIC("public");

    @JsonValue
    private final String value;

    KbVisibilityEnum(String value) {
        this.value = value;
    }

    @JsonCreator
    public static KbVisibilityEnum fromValue(String value) {
        for (KbVisibilityEnum scope : values()) {
            if (scope.value.equals(value)) {
                return scope;
            }
        }
        throw new IllegalArgumentException("不支持的 scope 值: " + value);
    }
}
