/*
 Navicat Premium Dump SQL

 Source Server         : rag-docker-mysql
 Source Server Type    : MySQL
 Source Server Version : 80405 (8.4.5)
 Source Host           : 192.168.188.6:13306
 Source Schema         : general_rag

 Target Server Type    : MySQL
 Target Server Version : 80405 (8.4.5)
 File Encoding         : 65001

 Date: 29/01/2026 11:34:51
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for audit_logs
-- ----------------------------
DROP TABLE IF EXISTS `audit_logs`;
CREATE TABLE `audit_logs`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '审计日志 ID',
  `user_id` bigint NOT NULL COMMENT '操作用户 ID',
  `action` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '操作类型（如 CREATE_KB / QUERY / UPLOAD_DOC）',
  `target_type` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '操作对象类型（KB / DOCUMENT / USER 等）',
  `target_id` bigint NULL DEFAULT NULL COMMENT '操作对象 ID',
  `detail` json NULL COMMENT '操作详情（扩展信息）',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
  `status` enum('SUCCESS','FAIL') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'SUCCESS',
  `error_message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `duration` bigint NULL DEFAULT 0,
  `display_message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_audit_user`(`user_id` ASC) USING BTREE,
  INDEX `idx_audit_target`(`target_type` ASC, `target_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 38548 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '系统操作审计日志表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for conversation_messages
-- ----------------------------
DROP TABLE IF EXISTS `conversation_messages`;
CREATE TABLE `conversation_messages`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '对话消息 ID',
  `session_id` bigint NOT NULL COMMENT '所属会话 ID，对应 query_sessions.id',
  `user_id` bigint NOT NULL COMMENT '用户 ID（冗余字段，便于查询与审计）',
  `kb_id` bigint NULL DEFAULT NULL COMMENT '当前使用的知识库 ID（冗余字段）',
  `role` enum('user','assistant','system') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '消息角色：user / assistant / system',
  `content` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '消息文本内容',
  `status` enum('pending','generating','completed','aborted','error') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'pending' COMMENT '消息的状态 \'pending\',\'generating\',\'completed\',\'aborted\',\'error\'',
  `model_id` bigint NOT NULL COMMENT '本次生成使用的模型（assistant 消息才有）',
  `prompt_tokens` int NULL DEFAULT NULL COMMENT 'prompt token 数',
  `completion_tokens` int NULL DEFAULT NULL COMMENT 'completion token 数',
  `total_tokens` int NULL DEFAULT NULL COMMENT '总 token 数',
  `rag_context` json NULL COMMENT 'RAG 检索上下文信息（命中的 chunk / doc / score 等）',
  `latency_ms` bigint NULL DEFAULT NULL COMMENT '本次生成耗时（毫秒）',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '消息创建时间',
  `is_deleted` int NOT NULL DEFAULT 0,
  `options` json NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_msg_session`(`session_id` ASC) USING BTREE,
  INDEX `idx_msg_model`(`model_id` ASC) USING BTREE,
  INDEX `idx_msg_user`(`user_id` ASC) USING BTREE,
  INDEX `idx_msg_kb`(`kb_id` ASC) USING BTREE,
  INDEX `idx_msg_role_time`(`role` ASC, `created_at` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5621 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = 'RAG 对话消息历史表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for document_chunks
-- ----------------------------
DROP TABLE IF EXISTS `document_chunks`;
CREATE TABLE `document_chunks`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '文档切片 ID',
  `document_id` bigint NOT NULL COMMENT '所属文档 ID',
  `kb_id` bigint NOT NULL COMMENT '所属知识库 ID（冗余字段，加速过滤）',
  `chunk_index` int NOT NULL COMMENT '文档内切片顺序号',
  `text` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '切片后的文本内容',
  `token_length` int NOT NULL COMMENT '该切片的 token 数',
  `vector_id` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'Milvus 中对应的向量 ID',
  `metadata` json NULL COMMENT '切片级元数据（页码、标题、来源等）',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_doc_chunk`(`document_id` ASC, `chunk_index` ASC) USING BTREE,
  INDEX `idx_chunks_kb`(`kb_id` ASC) USING BTREE,
  INDEX `idx_chunks_vector`(`vector_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 15416 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '文档切分后的最小语义单元表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for documents
-- ----------------------------
DROP TABLE IF EXISTS `documents`;
CREATE TABLE `documents`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '文档 ID',
  `kb_id` bigint NOT NULL COMMENT '所属知识库 ID',
  `file_path` varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'MinIO 中的对象存储路径',
  `file_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '原始文件名',
  `mime_type` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT '' COMMENT '文件 MIME 类型',
  `file_size` bigint NOT NULL COMMENT '文件大小（字节）',
  `uploader_id` bigint NOT NULL COMMENT '上传者用户 ID',
  `status` enum('processing','ready','failed') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'processing' COMMENT '处理状态：processing/ready/failed',
  `checksum` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '文件内容校验值（用于去重）',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` int NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_documents_kb`(`kb_id` ASC) USING BTREE,
  INDEX `idx_documents_status`(`status` ASC) USING BTREE,
  INDEX `idx_documents_uploader`(`uploader_id` ASC) USING BTREE,
  INDEX `file_name`(`file_name` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2487 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '知识库原始文档表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for kb_shares
-- ----------------------------
DROP TABLE IF EXISTS `kb_shares`;
CREATE TABLE `kb_shares`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '共享记录 ID',
  `kb_id` bigint NOT NULL COMMENT '知识库 ID',
  `user_id` bigint NOT NULL COMMENT '被授权用户 ID',
  `granted_by` bigint NOT NULL COMMENT '授权人用户 ID',
  `granted_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '授权时间',
  `is_deleted` int NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_kb_shares_user`(`user_id` ASC) USING BTREE,
  INDEX `idx_kb_shares_kb`(`kb_id` ASC) USING BTREE,
  INDEX `uk_kb_user`(`kb_id` ASC, `user_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 8 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '知识库共享与权限控制表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for knowledge_bases
-- ----------------------------
DROP TABLE IF EXISTS `knowledge_bases`;
CREATE TABLE `knowledge_bases`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '知识库 ID',
  `name` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '知识库名称',
  `owner_user_id` bigint NOT NULL COMMENT '知识库拥有者用户 ID',
  `workspace_id` bigint NULL DEFAULT NULL COMMENT '所属工作空间 ID',
  `visibility` enum('private','shared','public') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'private' COMMENT '可见性：private 私有，public 公共',
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '知识库描述',
  `system_prompt` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '系统提示词',
  `metadata` json NULL COMMENT '扩展元数据（如 embedding 模型、语言等）',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` int NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_kb_owner`(`owner_user_id` ASC) USING BTREE,
  INDEX `idx_kb_visibility`(`visibility` ASC) USING BTREE,
  INDEX `idx_kb_workspace`(`workspace_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 107 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '知识库主表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for model_permissions
-- ----------------------------
DROP TABLE IF EXISTS `model_permissions`;
CREATE TABLE `model_permissions`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '权限配置 ID',
  `role_id` int NOT NULL COMMENT '角色 ID，对应 roles.id',
  `model_id` bigint NOT NULL COMMENT '模型 ID，对应 models.id',
  `max_tokens` int NULL DEFAULT NULL COMMENT '单次请求最大 token 数',
  `qps_limit` int NULL DEFAULT NULL COMMENT '每秒最大请求数',
  `daily_token_limit` bigint NULL DEFAULT NULL COMMENT '每日 token 上限（NULL 表示不限）',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_role_model`(`role_id` ASC, `model_id` ASC) USING BTREE,
  INDEX `idx_mp_role`(`role_id` ASC) USING BTREE,
  INDEX `idx_mp_model`(`model_id` ASC) USING BTREE,
  CONSTRAINT `model_permissions_ibfk_1` FOREIGN KEY (`model_id`) REFERENCES `models` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 89 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '角色-模型配额与限流配置表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for models
-- ----------------------------
DROP TABLE IF EXISTS `models`;
CREATE TABLE `models`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '模型 ID',
  `name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '模型名称（如 gpt-4o / deepseek-r1）',
  `provider` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '模型提供方（openai / deepseek / local）',
  `max_context_tokens` int NULL DEFAULT NULL COMMENT '模型最大上下文长度',
  `enabled` tinyint(1) NOT NULL DEFAULT 1 COMMENT '模型是否启用（0 禁用，1 启用）',
  `metadata` json NULL COMMENT '模型扩展信息（如是否支持 function calling、vision 等）',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `kb_supported` int NULL DEFAULT 1 COMMENT '该模型是否支持知识库选择',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_model_name`(`name` ASC) USING BTREE,
  INDEX `idx_model_enabled`(`enabled` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 31 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '可用大模型定义表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for notifications
-- ----------------------------
DROP TABLE IF EXISTS `notifications`;
CREATE TABLE `notifications`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '公告id',
  `content` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '公告具体内容',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建按时间',
  `updated_at` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `display_type` enum('popup','normal') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT 'normal' COMMENT '前端展示方式，popup和marquee',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '前端公告' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for query_sessions
-- ----------------------------
DROP TABLE IF EXISTS `query_sessions`;
CREATE TABLE `query_sessions`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '会话 ID',
  `user_id` bigint NOT NULL COMMENT '用户 ID',
  `session_key` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '新的对话' COMMENT '前端/客户端会话标识',
  `last_active_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后一次活跃时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `workspace_id` bigint NOT NULL COMMENT '工作空间 ID',
  `is_deleted` int NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_sessions_user`(`user_id` ASC) USING BTREE,
  INDEX `uk_session_key`(`session_key` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 896 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = 'RAG 查询会话上下文表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for roles
-- ----------------------------
DROP TABLE IF EXISTS `roles`;
CREATE TABLE `roles`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '角色 ID',
  `name` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '角色名称（如 free / pro / enterprise）',
  `weight` int NOT NULL DEFAULT 0 COMMENT '角色权重，数值越大权限越高',
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '角色描述说明',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_roles_name`(`name` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户角色与等级定义表.' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '用户唯一 ID',
  `username` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '用户名（全局唯一）',
  `email` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '用户邮箱（全局唯一）',
  `pwd` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '用户密码',
  `role_id` int NOT NULL COMMENT '用户角色 ID，对应 roles.id',
  `workspace_id` bigint NULL DEFAULT NULL COMMENT '所属工作空间 ID',
  `status` enum('active','disabled') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'active' COMMENT '用户状态：active 启用，disabled 禁用',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` int NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_users_username`(`username` ASC) USING BTREE,
  UNIQUE INDEX `uk_users_email`(`email` ASC) USING BTREE,
  INDEX `idx_users_role`(`role_id` ASC) USING BTREE,
  INDEX `idx_users_workspace`(`workspace_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 185 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '系统用户表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for vector_collections
-- ----------------------------
DROP TABLE IF EXISTS `vector_collections`;
CREATE TABLE `vector_collections`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '向量集合 ID',
  `kb_id` bigint NOT NULL COMMENT '所属知识库 ID',
  `embedding_model` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '使用的 embedding 模型名称（如 text-embedding-3-large）',
  `collection_name` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'Milvus 中的 collection 名称',
  `dim` int NOT NULL COMMENT '向量维度',
  `metric_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'COSINE' COMMENT '向量距离度量方式（COSINE / L2 / IP）',
  `status` enum('active','deprecated') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'active' COMMENT '集合状态：active 当前使用，deprecated 已废弃',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `is_deleted` int NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_kb_collection`(`kb_id` ASC, `collection_name` ASC) USING BTREE,
  INDEX `idx_vector_kb`(`kb_id` ASC) USING BTREE,
  INDEX `idx_vector_model`(`embedding_model` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = 'Milvus 向量集合与知识库映射表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for workspace_members
-- ----------------------------
DROP TABLE IF EXISTS `workspace_members`;
CREATE TABLE `workspace_members`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `workspace_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `role` enum('owner','member') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'member',
  `joined_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `is_deleted` tinyint NULL DEFAULT 0,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `workspace_id`(`workspace_id` ASC, `user_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 220 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for workspaces
-- ----------------------------
DROP TABLE IF EXISTS `workspaces`;
CREATE TABLE `workspaces`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '工作空间 ID',
  `name` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '工作空间名称',
  `owner_user_id` bigint NOT NULL COMMENT '工作空间拥有者用户 ID',
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '工作空间描述',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `is_deleted` int NOT NULL DEFAULT 0,
  `can_edit` int NULL DEFAULT 1,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_workspace_owner`(`owner_user_id` ASC) USING BTREE,
  INDEX `uk_workspace_name_owner`(`name` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 203 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '多租户工作空间（Workspace）表' ROW_FORMAT = DYNAMIC;

SET FOREIGN_KEY_CHECKS = 1;
