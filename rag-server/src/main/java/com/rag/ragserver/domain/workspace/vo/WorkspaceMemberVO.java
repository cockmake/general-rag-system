package com.rag.ragserver.domain.workspace.vo;

import lombok.Data;
import java.util.Date;

@Data
public class WorkspaceMemberVO {
    private Long id;
    private Long userId;
    private String username;
    private String email;
    private String role;
    private Date joinedAt;
}
