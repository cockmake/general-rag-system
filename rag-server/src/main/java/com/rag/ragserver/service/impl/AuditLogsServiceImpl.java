package com.rag.ragserver.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.rag.ragserver.domain.AuditLogs;
import com.rag.ragserver.service.AuditLogsService;
import com.rag.ragserver.mapper.AuditLogsMapper;
import org.springframework.stereotype.Service;

/**
* @author make
* @description 针对表【audit_logs(系统操作审计日志表)】的数据库操作Service实现
* @createDate 2026-01-11 15:16:09
*/
@Service
public class AuditLogsServiceImpl extends ServiceImpl<AuditLogsMapper, AuditLogs>
    implements AuditLogsService{

}




