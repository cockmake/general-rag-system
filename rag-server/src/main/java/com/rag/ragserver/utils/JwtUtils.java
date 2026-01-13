package com.rag.ragserver.utils;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.security.Key;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

@Component
public class JwtUtils {
    @Value("${jwt.secret}")
    private String secret;

    @Value("${jwt.expiration}")
    private long defaultExpiration;

    // 定义 30 天的毫秒数 (30 * 24 * 60 * 60 * 1000)
    public static final long EXPIRATION_REMEMBER_ME = 2592000000L;

    public long getExpirationTime(boolean rememberMe) {
        return rememberMe ? EXPIRATION_REMEMBER_ME : defaultExpiration;
    }

    /**
     * 生成 Key 对象
     */
    private Key getSigningKey() {
        return Keys.hmacShaKeyFor(secret.getBytes());
    }

    /**
     * 生成 Token
     * 修改：增加 userId 参数，并将 userId 和 username 存入 Claims
     * @param userId 用户ID
     * @param username 用户名
     * @param rememberMe 是否记住我
     * @return JWT 字符串
     */
    public String generateToken(Long userId, String username, boolean rememberMe, String jti) {
        Map<String, Object> claims = new HashMap<>();
        claims.put("userId", userId);
        claims.put("username", username);

        // 核心逻辑：根据参数决定过期时间长度
        long expireTime = rememberMe ? EXPIRATION_REMEMBER_ME : defaultExpiration;

        return createToken(claims, username, expireTime, jti);
    }

    private String createToken(Map<String, Object> claims, String subject, long expireTime, String jti) {
        return Jwts.builder()
                .setClaims(claims)
                .setSubject(subject)
                .setId(jti) // Add unique ID
                .setIssuedAt(new Date(System.currentTimeMillis()))
                .setExpiration(new Date(System.currentTimeMillis() + expireTime))
                .signWith(getSigningKey(), SignatureAlgorithm.HS256)
                .compact();
    }

    /**
     * 检查 Token 是否过期
     */
    public boolean isTokenExpired(String token) {
        return extractAllClaims(token).getExpiration().before(new Date());
    }

    /**
     * 解析 Token 获取所有 Claims
     * 修改：改为 public 供拦截器使用
     */
    public Claims extractAllClaims(String token) {
        return Jwts.parserBuilder()
                .setSigningKey(getSigningKey())
                .build()
                .parseClaimsJws(token)
                .getBody();
    }
}