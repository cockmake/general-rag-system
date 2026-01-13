package com.rag.ragserver.mapper;

import com.rag.ragserver.domain.ConversationMessages;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import java.util.Date;

/**
* @author make
* @description 针对表【conversation_messages(RAG 对话消息历史表)】的数据库操作Mapper
* @createDate 2026-01-02 23:06:15
* @Entity com.rag.ragserver.domain.ConversationMessages
*/
public interface ConversationMessagesMapper extends BaseMapper<ConversationMessages> {

    @Select("SELECT SUM(total_tokens) FROM conversation_messages WHERE created_at >= #{startTime}")
    Long sumTotalTokensSince(@Param("startTime") Date startTime);

    @Select("SELECT SUM(total_tokens) FROM conversation_messages WHERE created_at >= #{startTime} AND user_id = #{userId}")
    Long sumUserTotalTokensSince(@Param("startTime") Date startTime, @Param("userId") Long userId);
}




