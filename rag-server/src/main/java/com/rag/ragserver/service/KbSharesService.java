package com.rag.ragserver.service;

import com.rag.ragserver.domain.KbShares;
import com.baomidou.mybatisplus.extension.service.IService;
import com.rag.ragserver.domain.kb.vo.KbShareUserVO;

import java.util.List;

/**
* @author make
* @description 针对表【kb_shares(知识库共享与权限控制表)】的数据库操作Service
* @createDate 2025-12-31 01:13:35
*/
public interface KbSharesService extends IService<KbShares> {
    
    /**
     * 邀请用户访问知识库
     * @param kbId 知识库ID
     * @param targetUserId 被邀请用户ID
     * @param operatorUserId 操作者ID
     */
    void inviteUser(Long kbId, Long targetUserId, Long operatorUserId);
    
    /**
     * 获取知识库的被邀请用户列表
     * @param kbId 知识库ID
     * @return 被邀请用户列表
     */
    List<KbShareUserVO> getInvitedUsers(Long kbId);
    
    /**
     * 移除被邀请用户
     * @param kbId 知识库ID
     * @param userId 用户ID
     * @param operatorUserId 操作者ID
     */
    void removeInvitedUser(Long kbId, Long userId, Long operatorUserId);
}
