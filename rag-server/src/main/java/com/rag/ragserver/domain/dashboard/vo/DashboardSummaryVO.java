package com.rag.ragserver.domain.dashboard.vo;

import lombok.Data;

@Data
public class DashboardSummaryVO {
    private Long userCount;
    private Long kbCount;
    private Long documentCount;
    private Long sessionCount;
    private Long todayTokenUsage;
}
