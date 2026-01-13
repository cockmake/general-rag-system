package com.rag.ragserver.service;

public interface EmailService {
    void sendVerificationCode(String to, String code);
}
