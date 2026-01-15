<script setup>
import { GithubOutlined } from '@ant-design/icons-vue';
</script>

<template>
  <div class="auth-layout">
    <div class="auth-intro">
      <div class="intro-content">
        <div class="logo-container">
          <img src="@/assets/logo.png" alt="Logo" class="intro-logo"/>
          <h1>RAG 知识库问答系统</h1>
        </div>
        <div class="intro-desc">
          <p>基于先进大语言模型的智能问答助手</p>
          <p>构建您的专属知识库，实现精准、高效的知识检索与问答。</p>
          <ul class="feature-list">
            <li>📚 智能文档解析与管理</li>
            <li>💡 精准语义检索</li>
            <li>🤖 多模型支持</li>
            <li>🔒 私有化部署，数据安全</li>
          </ul>
          
          <div class="intro-footer">
            <a href="https://github.com/cockmake/general-rag-system" target="_blank" class="github-link">
              <github-outlined />
              <span>GitHub Open Source</span>
            </a>
          </div>
        </div>
      </div>
    </div>
    <div class="auth-form-container">
      <slot></slot>
    </div>
  </div>
</template>

<style scoped>
.auth-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.auth-intro {
  flex: 3;
  background: url('@/assets/login_bg.jpg') no-repeat center center;
  background-size: cover;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.auth-intro::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6); /* Overlay to make text readable */
}

.intro-content {
  position: relative;
  z-index: 1;
  max-width: 600px;
  padding: 40px;
}

.logo-container {
  display: flex;
  align-items: center;
  margin-bottom: 32px;
}

.intro-logo {
  height: 64px;
  margin-right: 24px;
}

.intro-content h1 {
  font-size: 32px;
  font-weight: bold;
  margin: 0;
  color: #fff;
}

.intro-desc {
  font-size: 18px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.9);
}

.feature-list {
  list-style: none;
  padding: 0;
  margin-top: 32px;
}

.feature-list li {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  font-size: 16px;
}

.intro-footer {
  margin-top: 48px;
}

.github-link {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 16px;
  text-decoration: none;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 10px 20px;
  border-radius: 6px;
  transition: all 0.3s;
  background: rgba(0, 0, 0, 0.2);
}

.github-link:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.8);
}

.auth-form-container {
  flex: 2;
  width: 480px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  position: relative;
  box-shadow: -4px 0 16px rgba(0, 0, 0, 0.05);
}

@media (max-width: 768px) {
  .auth-intro {
    display: none;
  }
  
  .auth-form-container {
    width: 100%;
  }
}
</style>
