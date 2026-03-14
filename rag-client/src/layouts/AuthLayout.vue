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
      <div class="mobile-intro">
        <h3 class="mobile-intro-title">RAG 知识库问答系统</h3>
        <p class="mobile-intro-subtitle">构建您的专属知识库，实现精准、高效的知识检索与问答。</p>
        <ul class="mobile-feature-list">
          <li>📚 智能文档解析与管理</li>
          <li>💡 精准语义检索</li>
          <li>🤖 多模型支持</li>
          <li>🔒 私有化部署，数据安全</li>
        </ul>
      </div>
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

.mobile-intro {
  display: none;
}

@media (max-width: 768px) {
  .auth-layout {
    min-height: 100vh;
    height: auto;
    background:
      radial-gradient(120% 80% at 20% 0%, rgba(22, 119, 255, 0.2), transparent 60%),
      radial-gradient(100% 80% at 100% 100%, rgba(114, 46, 209, 0.22), transparent 60%),
      linear-gradient(145deg, #f5f8ff 0%, #eef3ff 55%, #f6f9ff 100%);
  }

  .auth-intro {
    display: none;
  }

  .auth-form-container {
    width: min(100%, 460px);
    flex-direction: column;
    align-items: stretch;
    justify-content: flex-start;
    margin: 12px;
    border-radius: 22px;
    background: rgba(255, 255, 255, 0.92);
    box-shadow: 0 20px 44px rgba(33, 62, 143, 0.18);
    backdrop-filter: blur(8px);
  }

  .mobile-intro {
    display: block;
    margin: 20px 16px 4px;
    padding: 14px 14px 12px;
    border-radius: 14px;
    background: linear-gradient(135deg, #e8f0ff 0%, #f2ebff 100%);
    box-shadow: inset 0 0 0 1px rgba(22, 119, 255, 0.1);
  }

  .mobile-intro-title {
    margin: 0;
    font-size: 16px;
    font-weight: 700;
    color: #1c2d4a;
  }

  .mobile-intro-subtitle {
    margin: 6px 0 10px;
    font-size: 12px;
    line-height: 1.5;
    color: #53627a;
  }

  .mobile-feature-list {
    margin: 0;
    padding: 0;
    list-style: none;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px 10px;
  }

  .mobile-feature-list li {
    font-size: 12px;
    color: #2f3d56;
    line-height: 1.4;
  }
}

@media (max-width: 480px) {
  .auth-form-container {
    margin: 10px;
    border-radius: 18px;
  }

  .mobile-intro {
    margin: 16px 12px 2px;
    padding: 12px;
  }

  .mobile-intro-title {
    font-size: 15px;
  }

  .mobile-feature-list {
    grid-template-columns: 1fr;
    gap: 6px;
  }
}
</style>
