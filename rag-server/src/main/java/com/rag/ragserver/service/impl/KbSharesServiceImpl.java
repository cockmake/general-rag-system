package com.rag.ragserver.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.rag.ragserver.domain.KbShares;
import com.rag.ragserver.domain.KnowledgeBases;
import com.rag.ragserver.domain.Users;
import com.rag.ragserver.domain.kb.vo.KbShareUserVO;
import com.rag.ragserver.exception.BusinessException;
import com.rag.ragserver.service.KbSharesService;
import com.rag.ragserver.mapper.KbSharesMapper;
import com.rag.ragserver.service.KnowledgeBasesService;
import com.rag.ragserver.service.UsersService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Date;
import java.util.List;
import java.util.stream.Collectors;

/**
* @author make
* @description 针对表【kb_shares(知识库共享与权限控制表)】的数据库操作Service实现
* @createDate 2025-12-31 01:13:35
*/
@Service
@RequiredArgsConstructor
public class KbSharesServiceImpl extends ServiceImpl<KbSharesMapper, KbShares>
    implements KbSharesService{

    private final KnowledgeBasesService knowledgeBasesService;
    private final UsersService usersService;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void inviteUser(Long kbId, Long targetUserId, Long operatorUserId) {
        // 1. 检查知识库是否存在
        KnowledgeBases kb = knowledgeBasesService.getById(kbId);
        if (kb == null) {
            throw new BusinessException(404, "知识库不存在");
        }
        
        // 2. 检查操作者是否是知识库拥有者
        if (!kb.getOwnerUserId().equals(operatorUserId)) {
            throw new BusinessException(403, "只有知识库拥有者可以邀请用户");
        }
        
        // 3. 检查知识库是否为私有
        if (!"private".equals(kb.getVisibility())) {
            throw new BusinessException(400, "只有私有知识库可以邀请用户");
        }
        
        // 4. 检查被邀请用户是否存在
        Users targetUser = usersService.getById(targetUserId);
        if (targetUser == null) {
            throw new BusinessException(404, "目标用户不存在");
        }
        
        // 5. 检查是否是知识库拥有者本人
        if (targetUserId.equals(operatorUserId)) {
            throw new BusinessException(400, "不能邀请自己");
        }
        
        // 6. 检查是否已经邀请过
        LambdaQueryWrapper<KbShares> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(KbShares::getKbId, kbId)
               .eq(KbShares::getUserId, targetUserId);
        long count = this.count(wrapper);
        if (count > 0) {
            throw new BusinessException(400, "该用户已被邀请");
        }
        
        // 7. 创建邀请记录
        KbShares share = new KbShares();
        share.setKbId(kbId);
        share.setUserId(targetUserId);
        share.setGrantedBy(operatorUserId);
        // share.setGrantedAt(new Date());
        
        if (!this.save(share)) {
            throw new BusinessException(500, "邀请用户失败");
        }
    }

    @Override
    public List<KbShareUserVO> getInvitedUsers(Long kbId) {
        // 1. 查询所有被邀请的用户记录
        LambdaQueryWrapper<KbShares> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(KbShares::getKbId, kbId)
               .orderByDesc(KbShares::getGrantedAt);
        List<KbShares> shares = this.list(wrapper);
        
        // 2. 转换为 VO
        return shares.stream().map(share -> {
            KbShareUserVO vo = new KbShareUserVO();
            vo.setId(share.getId());
            vo.setUserId(share.getUserId());
            vo.setGrantedBy(share.getGrantedBy());
            vo.setGrantedAt(share.getGrantedAt());
            
            // 查询用户信息
            Users user = usersService.getById(share.getUserId());
            if (user != null) {
                vo.setUsername(user.getUsername());
                vo.setEmail(user.getEmail());
            }
            
            // 查询授权人信息
            Users grantedByUser = usersService.getById(share.getGrantedBy());
            if (grantedByUser != null) {
                vo.setGrantedByUsername(grantedByUser.getUsername());
            }
            
            return vo;
        }).collect(Collectors.toList());
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void removeInvitedUser(Long kbId, Long userId, Long operatorUserId) {
        // 1. 检查知识库是否存在
        KnowledgeBases kb = knowledgeBasesService.getById(kbId);
        if (kb == null) {
            throw new BusinessException(404, "知识库不存在");
        }
        
        // 2. 检查操作者是否是知识库拥有者
        if (!kb.getOwnerUserId().equals(operatorUserId)) {
            throw new BusinessException(403, "只有知识库拥有者可以移除被邀请用户");
        }
        
        // 3. 删除邀请记录
        LambdaQueryWrapper<KbShares> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(KbShares::getKbId, kbId)
               .eq(KbShares::getUserId, userId);
        
        if (!this.remove(wrapper)) {
            throw new BusinessException(500, "移除用户失败");
        }
    }
}




