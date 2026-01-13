package com.rag.ragserver.domain.workspace.vo;

import lombok.Data;
import java.util.Date;

@Data
public class WorkspaceVO {
    private Long id;
    private String name;
    private Long ownerUserId;
    private String description;
    private Date createdAt;
}