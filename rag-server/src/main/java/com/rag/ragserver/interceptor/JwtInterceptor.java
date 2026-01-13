package com.rag.ragserver.interceptor;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.rag.ragserver.domain.Users;
import com.rag.ragserver.domain.Workspaces;
import com.rag.ragserver.exception.BusinessException;
import com.rag.ragserver.service.UsersService;
import com.rag.ragserver.service.WorkspacePermissionService;
import com.rag.ragserver.service.WorkspacesService;
import com.rag.ragserver.utils.JwtUtils;
import io.jsonwebtoken.Claims;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.util.HashMap;
import java.util.Map;

@Slf4j
@Component
@RequiredArgsConstructor
public class JwtInterceptor implements HandlerInterceptor {

    private final JwtUtils jwtUtils;
    private final UsersService usersService;
    private final StringRedisTemplate redisTemplate;
    private final WorkspacePermissionService workspacePermissionService;
    private final WorkspacesService workspacesService;

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {

        // 1. 对于 OPTIONS 请求（跨域预检），直接放行
        if ("OPTIONS".equals(request.getMethod())) {
            return true;
        }

        // 2. 从 Header 中获取 Token
        String token = request.getHeader("Authorization");

        // 3. 校验 Token 是否存在
        if (token == null || token.isEmpty()) {
            throw new BusinessException(401, "未登录，请先登录");
        }

        // 4. 处理 "Bearer " 前缀（如果前端传了的话，通常前端会带，这里做一个兼容处理）
        if (token.startsWith("Bearer ")) {
            token = token.substring(7);
        }

        // 5. 校验 Token 有效性
        // 这里调用 JwtUtils 解析，如果过期或无效，jjwt 库通常会直接抛出异常
        // 只要能正常解析出 username，就说明没过期且签名正确
        if (jwtUtils.isTokenExpired(token)) {
            throw new BusinessException(401, "Token已过期或无效，请重新登录");
        }
        Claims claims = jwtUtils.extractAllClaims(token);

        // 校验 Redis 中是否存在该 Token (JTI)
        String jti = claims.getId();
        if (jti == null || !Boolean.TRUE.equals(redisTemplate.hasKey("login:token:" + jti))) {
            throw new BusinessException(401, "Token已失效，请重新登录");
        }

        Long userId = claims.get("userId", Long.class);

        // 去数据库查询用户是否存在及状态
        // 优化：可以把用户信息也缓存到 Redis，减少数据库查询
        Users user = usersService.getById(userId);
        if (user == null || !"active".equals(user.getStatus())) {
            throw new BusinessException(403, "用户不存在或已被禁用");
        }

        // 可以把用户信息存入 request，方便后续 Controller 使用
        request.setAttribute("userId", userId);
        request.setAttribute("roleId", user.getRoleId());

        // 判断用户是否还在当前工作空间，如果不在就告知用户进行切换
        // 如果是请求workspace列表，或者切换workspace的接口，便于用户获取或切换工作空间，放行
        // /workspaces/list 和 /workspaces/{workspaceId}/switch

        Long currentWorkspaceId = user.getWorkspaceId();
        request.setAttribute("workspaceId", currentWorkspaceId);

        // 如果是请求workspace列表或切换接口，直接放行，便于用户获取或切换工作空间
        if (request.getRequestURI().endsWith("/workspaces/list") || request.getRequestURI().contains("/workspaces/") && request.getRequestURI().endsWith("/switch")) {
            return true;
        }

        // 验证用户的当前工作空间是否有效且用户仍是成员
        Workspaces currentWorkspace = workspacesService.getById(currentWorkspaceId);
        if (currentWorkspace == null || !workspacePermissionService.isMemberOfWorkspace(currentWorkspaceId, userId)) {
            throw new BusinessException(403, "您已不在当前工作空间，请重新选择工作空间");
        }

        return true; // 放行

    }
}
