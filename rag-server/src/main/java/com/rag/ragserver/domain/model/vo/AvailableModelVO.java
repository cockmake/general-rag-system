package com.rag.ragserver.domain.model.vo;

import lombok.Data;

@Data
public class AvailableModelVO {
    /** 模型 ID */
    private Long modelId;

    /** 模型名称，如 gpt-4o */
    private String modelName;

    /** 提供方，如 openai / deepseek */
    private String provider;

    /** 模型最大上下文长度 */
    private Integer maxContextTokens;

    /** 当前角色在该模型上的单次最大 token */
    private Integer maxTokens;

    /** QPS 限制 */
    private Integer qpsLimit;

    /** 每日 token 上限（可能为 null，表示不限） */
    private Long dailyTokenLimit;
}
