package com.rag.ragserver.domain.session;

public enum SessionGroupType {

    TODAY("今天"),
    YESTERDAY("昨天"),
    EARLIER("更早");

    private final String displayName;

    SessionGroupType(String displayName) {
        this.displayName = displayName;
    }

    public String getDisplayName() {
        return displayName;
    }
}
