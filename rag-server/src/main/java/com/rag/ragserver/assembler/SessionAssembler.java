package com.rag.ragserver.assembler;

import com.rag.ragserver.domain.QuerySessions;
import com.rag.ragserver.domain.session.SessionGroupType;
import com.rag.ragserver.domain.session.vo.SessionCursorVO;
import com.rag.ragserver.domain.session.vo.SessionGroupVO;
import com.rag.ragserver.domain.session.vo.SessionItemVO;
import com.rag.ragserver.domain.session.vo.SessionListVO;

import java.time.LocalDate;
import java.time.ZoneId;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class SessionAssembler {
    public static SessionListVO toVO(List<QuerySessions> sessions, boolean hasMore) {

        Map<SessionGroupType, List<SessionItemVO>> groupMap = new LinkedHashMap<>();

        LocalDate today = LocalDate.now();
        LocalDate yesterday = today.minusDays(1);

        for (QuerySessions s : sessions) {
            LocalDate date = s.getLastActiveAt()
                    .toInstant()
                    .atZone(ZoneId.systemDefault())
                    .toLocalDate();
            SessionGroupType group =
                    date.equals(today) ? SessionGroupType.TODAY :
                            date.equals(yesterday) ? SessionGroupType.YESTERDAY :
                                    SessionGroupType.EARLIER;

            groupMap
                    .computeIfAbsent(group, k -> new ArrayList<>())
                    .add(new SessionItemVO(s));
        }

        List<SessionGroupVO> groups = new ArrayList<>();
        groupMap.forEach((k, v) -> groups.add(new SessionGroupVO(k, v)));

        SessionCursorVO cursor = null;
        if (!sessions.isEmpty()) {
            QuerySessions last = sessions.get(sessions.size() - 1);
            cursor = new SessionCursorVO(
                    last.getLastActiveAt()
                            .toInstant()
                            .atZone(ZoneId.systemDefault())
                            .toLocalDateTime(),
                    last.getId()
            );
        }

        return new SessionListVO(groups, hasMore, cursor);
    }
}
