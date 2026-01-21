package com.rag.ragserver.dto;

import lombok.Data;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Min;

@Data
public class SessionSearchQuery {
    @NotBlank(message = "搜索关键词不能为空")
    private String keyword;
    
    @Min(value = 1, message = "Limit必须大于0")
    private int limit = 20;
    
    @Min(value = 0, message = "Offset不能小于0")
    private int offset = 0;
}
