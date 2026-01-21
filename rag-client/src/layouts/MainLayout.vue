<script setup>
import {ref, watch, computed} from 'vue'
import {useRouter, useRoute} from 'vue-router'
import SessionList from '@/components/SessionList.vue'
import {useThemeStore} from '@/stores/theme'
import {useUserStore} from '@/stores/user'
import {
  BulbOutlined, 
  BulbFilled, 
  LogoutOutlined, 
  UserOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  GithubOutlined
} from '@ant-design/icons-vue';
// 引入本地静态资源 URL
import lightThemeUrl from '@/assets/github-markdown.min.css?url';
import darkThemeUrl from '@/assets/github-markdown-dark.min.css?url';
import workspaceApi from '@/api/workspaceApi.js';

const router = useRouter()
const route = useRoute()
const selectedKeys = ref([])
const themeStore = useThemeStore();
const userStore = useUserStore();
const currentWorkspace = ref(null)
const isFooterExpanded = ref(false) // 控制底部区域展开/收起
const collapsed = ref(false) // 控制侧边栏收起/展开

// 加载当前工作空间信息
const loadCurrentWorkspace = async () => {
  try {
    const data = await workspaceApi.getWorkspaces()
    currentWorkspace.value = data.current
  } catch (error) {
    console.error('加载工作空间失败:', error)
  }
}

// 计算用户显示名称
const userDisplayName = computed(() => {
  return userStore.user?.email || userStore.user?.username || '未登录'
})

// 计算工作空间显示名称
const workspaceDisplayName = computed(() => {
  return currentWorkspace.value?.name || '未选择工作空间'
})

// 切换底部区域展开状态
const toggleFooter = () => {
  isFooterExpanded.value = !isFooterExpanded.value
}

// 切换侧边栏收起/展开
const toggleCollapsed = () => {
  collapsed.value = !collapsed.value
}

// 退出登录
const handleLogout = () => {
  userStore.logout()
}

// 动态加载 CSS 的函数
const loadMarkdownTheme = (isDark) => {
  const existingLink = document.getElementById('markdown-theme-css');
  if (existingLink) {
    existingLink.remove();
  }

  const link = document.createElement('link');
  link.id = 'markdown-theme-css';
  link.rel = 'stylesheet';
  // 使用本地资源 URL
  link.href = isDark ? darkThemeUrl : lightThemeUrl;
  document.head.appendChild(link);
};

// 监听主题变化
watch(
    () => themeStore.isDark,
    (newVal) => {
      loadMarkdownTheme(newVal);
    },
    {immediate: true}
);

/**
 * 同步菜单选中状态
 */
watch(
    () => route.path,
    () => {
      if (route.path.startsWith('/chat/new')) {
        selectedKeys.value = ['new-chat']
      } else if (route.path.startsWith('/dashboard')) {
        selectedKeys.value = ['dashboard']
      } else if (route.path.startsWith('/kb')) {
        selectedKeys.value = ['kb']
      } else if (route.path.startsWith('/search')) {
        selectedKeys.value = ['search']
      } else if (route.path.startsWith('/workspaces')) {
        selectedKeys.value = ['workspaces']
      } else {
        selectedKeys.value = []
      }
    },
    {immediate: true}
)

// 初始化加载工作空间信息
loadCurrentWorkspace()

const go = (path) => {
  router.push(path)
}
</script>

<template>
  <a-layout style="min-height: 100vh">
    <!-- 移动端遮罩层 -->
    <div 
      v-if="!collapsed" 
      class="sidebar-overlay" 
      @click="toggleCollapsed"
    ></div>
    
    <a-layout-sider 
      v-model:collapsed="collapsed"
      :width="240" 
      :collapsed-width="64"
      :theme="themeStore.isDark ? 'dark' : 'light'" 
      style="position: fixed; left: 0; top: 0; bottom: 0; height: 100vh; z-index: 100;"
      collapsible
      :trigger="null">
      <div class="sidebar-container">
        <!-- Logo -->
        <div class="logo"
             :style="{ color: themeStore.isDark ? '#fff' : 'inherit', borderBottomColor: themeStore.isDark ? '#303030' : '#f0f0f0' }">
          <img v-if="!collapsed" src="@/assets/logo.png" alt="Logo" style="height: 50px"/>
          <img v-else src="@/assets/logo.png" alt="Logo" style="height: 32px"/>
          <span v-if="!collapsed">RAG 系统</span>
        </div>
        
        <!-- 功能菜单 -->
        <a-menu mode="inline" :selectedKeys="selectedKeys" :theme="themeStore.isDark ? 'dark' : 'light'" :inline-collapsed="collapsed">
          <a-menu-item key="new-chat" @click="go('/chat/new')">
            <template #icon>
              <span style="font-size: 16px;">➕</span>
            </template>
            新聊天
          </a-menu-item>
          <a-menu-item key="dashboard" @click="go('/dashboard')">
            <template #icon>
              <span style="font-size: 16px;">📊</span>
            </template>
            Dashboard
          </a-menu-item>

          <a-menu-item key="kb" @click="go('/kb')">
            <template #icon>
              <span style="font-size: 16px;">📚</span>
            </template>
            知识库
          </a-menu-item>
          <a-menu-item key="workspaces" @click="go('/workspaces')">
            <template #icon>
              <span style="font-size: 16px;">🏢</span>
            </template>
            工作空间
          </a-menu-item>
          <a-menu-item key="search" @click="go('/search')">
            <template #icon>
              <span style="font-size: 16px;">🔍</span>
            </template>
            搜索对话
          </a-menu-item>
        </a-menu>

        <!-- 最近会话（独立区域） - 收起时隐藏 -->
        <div v-if="!collapsed" class="session-wrapper">
          <div class="session-title">最近聊天</div>
          <div class="session-list-container">
            <SessionList/>
          </div>
        </div>

        <!-- 底部信息区域 -->
        <div class="sidebar-footer" :style="{ 
          borderTopColor: themeStore.isDark ? '#303030' : '#f0f0f0',
          backgroundColor: themeStore.isDark ? '#141414' : '#fafafa'}">

          <!-- 展开的操作按钮区域（在上方） - 仅在未收起时显示 -->
          <transition name="slide-fade-up">
            <div v-if="isFooterExpanded && !collapsed" class="action-buttons">
              <!-- 收起/展开按钮 -->
              <a-button type="text" @click="toggleCollapsed" class="collapse-btn">
                <template #icon>
                  <menu-fold-outlined v-if="!collapsed" />
                  <menu-unfold-outlined v-else />
                </template>
                <span v-if="!collapsed">收起侧边栏</span>
              </a-button>
              <!-- 主题切换 -->
              <a-button type="text" @click.stop="themeStore.toggleTheme" :title="themeStore.isDark ? '切换亮色主题' : '切换暗色主题'">
                <template #icon>
                  <bulb-filled v-if="themeStore.isDark"/>
                  <bulb-outlined v-else/>
                </template>
                {{ themeStore.isDark ? '切换亮色' : '切换暗色' }}
              </a-button>
              
              <!-- GitHub 开源地址 -->
              <a-button type="text" href="https://github.com/cockmake/general-rag-system" target="_blank" title="GitHub 开源地址">
                <template #icon>
                  <github-outlined />
                </template>
                GitHub 开源地址
              </a-button>

              <!-- 退出登录 -->
              <a-button type="text" danger @click.stop="handleLogout" title="退出登录">
                <template #icon>
                  <logout-outlined />
                </template>
                退出登录
              </a-button>
            </div>
          </transition>
          
          <!-- 可点击的信息展示区域（在下方） - 仅在未收起时显示 -->
          <div v-if="!collapsed" class="footer-info-section" @click="toggleFooter" :style="{ cursor: 'pointer' }">
            <!-- 用户信息 -->
            <div class="user-info" :style="{ color: themeStore.isDark ? '#fff' : '#000' }">
              <user-outlined style="margin-right: 8px;" />
              <span class="user-name">{{ userDisplayName }}</span>
            </div>
            
            <!-- 工作空间信息 -->
            <div class="workspace-info" :style="{ color: themeStore.isDark ? '#999' : '#666' }">
              <span>🏢 {{ workspaceDisplayName }}</span>
            </div>
          </div>
          
          <!-- 收起状态下的用户图标 -->
          <div v-else class="footer-collapsed-icon" @click="toggleCollapsed" :style="{ 
            color: themeStore.isDark ? '#fff' : '#000',
            cursor: 'pointer'
          }">
            <user-outlined style="font-size: 20px;" />
          </div>
        </div>
      </div>
    </a-layout-sider>

    <a-layout :style="{ marginLeft: collapsed ? '64px' : '240px', transition: 'margin-left 0.2s' }">
      <!-- 移动端展开按钮 -->
      <a-button 
        v-if="collapsed"
        class="mobile-menu-btn"
        type="primary" 
        shape="circle"
        @click="toggleCollapsed"
      >
        <template #icon>
          <menu-unfold-outlined />
        </template>
      </a-button>
      
      <a-layout-content style="padding: 0">
        <router-view/>
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<style scoped>
.sidebar-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
}

.logo {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  border-bottom: 1px solid #f0f0f0;
  flex-shrink: 0;
  gap: 8px;
  transition: all 0.2s;
}

.session-wrapper {
  border-top: 1px solid #f0f0f0;
  padding: 8px 4px;
  overflow: hidden;
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.session-title {
  font-size: 12px;
  color: #999;
  padding: 4px 8px;
  flex-shrink: 0;
}

.session-list-container {
  flex: 1;
  min-height: 0;
  overflow: hidden; /* Ensure SessionList's height:100% works against this */
}

.sidebar-footer {
  flex-shrink: 0;
  padding: 12px 16px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.collapse-btn {
  justify-content: flex-start;
  text-align: left;
  width: 100%;
}

.footer-info-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 4px 0;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.footer-info-section:hover {
  background-color: rgba(0, 0, 0, 0.04);
}

[data-theme="dark"] .footer-info-section:hover {
  background-color: rgba(255, 255, 255, 0.08);
}

.footer-collapsed-icon {
  display: flex;
  justify-content: center;
  padding: 8px 0;
  transition: all 0.2s;
}

.footer-collapsed-icon:hover {
  background-color: rgba(0, 0, 0, 0.04);
  border-radius: 4px;
}

[data-theme="dark"] .footer-collapsed-icon:hover {
  background-color: rgba(255, 255, 255, 0.08);
}

.user-info {
  display: flex;
  align-items: center;
  font-size: 14px;
  font-weight: 500;
}

.user-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.workspace-info {
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding-left: 24px;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 4px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

[data-theme="dark"] .action-buttons {
  border-bottom-color: rgba(255, 255, 255, 0.12);
}

.action-buttons .ant-btn {
  justify-content: flex-start;
  text-align: left;
}

/* 向上滑动淡入淡出动画 */
.slide-fade-up-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-up-leave-active {
  transition: all 0.2s ease-in;
}

.slide-fade-up-enter-from {
  transform: translateY(10px);
  opacity: 0;
}

.slide-fade-up-leave-to {
  transform: translateY(10px);
  opacity: 0;
}

/* 移动端响应式 */
@media (max-width: 768px) {
  /* 在移动端，侧边栏在收起时完全隐藏 */
  .sidebar-container {
    overflow-x: hidden;
  }
}

/* 移动端遮罩层 */
.sidebar-overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 99;
}

/* 移动端展开按钮 */
.mobile-menu-btn {
  display: none;
  position: fixed;
  top: 16px;
  left: 80px;
  z-index: 101;
}

@media (max-width: 768px) {
  .mobile-menu-btn {
    display: block;
  }
  
  .sidebar-overlay {
    display: block;
  }
}

</style>
