<script setup>
import {ref, onMounted, computed, watch} from 'vue'
import {useRouter} from 'vue-router'
import {message} from 'ant-design-vue'
import {Sender} from 'ant-design-x-vue'
import {CommentOutlined, RobotOutlined, DatabaseOutlined} from '@ant-design/icons-vue'

import {awaitSessionTitle, fetchAvailableModels, startChat} from '@/api/chatApi'
import {models, groupedModels, selectedModel, selectedKb, loadKbs} from "@/vars.js";
import {events} from "@/events.js";
import KbSelector from "@/components/KbSelector.vue";
import { useThemeStore } from '@/stores/theme';

const router = useRouter()
const themeStore = useThemeStore();

const loading = ref(false)

onMounted(async () => {
  // 默认选第一个模型
  models.value = await fetchAvailableModels().then()
  selectedModel.value = selectedModel.value || models.value[0]?.modelId || null
  // 加载知识库列表
  await loadKbs()
})

const isKbSupported = computed(() => {
  if (!selectedModel.value) return false
  const modelObj = models.value.find(m => m.modelId === selectedModel.value)
  if (!modelObj) return false
  return modelObj.kbSupported || false
})

watch(selectedModel, () => {
  if (!isKbSupported.value) {
    selectedKb.value = null
  }
})

const onSend = async (text) => {
  if (!selectedModel.value) {
    message.warning('请选择模型')
    return
  }

  loading.value = true
  try {
    const res = await startChat({
      modelId: selectedModel.value,
      question: text,
      kbId: isKbSupported.value ? (selectedKb.value || undefined) : undefined
    })
    let {sessionId} = res
    if (sessionId) {
      awaitSessionTitle(sessionId, (title) => {
        events.emit('sessionTitleUpdated', {
          sessionId,
          title
        })
      })
      events.emit('sessionListRefresh')
      router.replace(`/chat/${res.sessionId}`).then(() => {
        message.success('新聊天已创建')
        // 并刷新SessionList组件的数据
      })
    }
  } finally {
    loading.value = false
  }
}
</script>


<template>
  <div class="new-chat-container" :class="{ 'is-dark': themeStore.isDark }">
    <div class="content-wrapper">
      <!-- 欢迎区域 -->
      <div class="welcome-section">
        <div class="welcome-icon">
          <CommentOutlined />
        </div>
        <h1 class="welcome-title">开始新的对话</h1>
        <p class="welcome-subtitle">选择模型和知识库，开启智能对话体验</p>
      </div>

      <!-- 配置卡片 -->
      <a-card class="config-card" :bordered="false">
        <div class="config-section">
          <div class="config-item">
            <div class="config-label">
              <RobotOutlined class="config-icon" />
              <span>选择模型</span>
            </div>
            <a-select
                v-model:value="selectedModel"
                class="config-select"
                placeholder="请选择对话模型"
                size="large"
                style="width: 280px">
              <a-select-opt-group
                  v-for="(list, provider) in groupedModels"
                  :key="provider"
                  :label="provider.toUpperCase()">
                <a-select-option
                    v-for="m in list"
                    :key="m.modelId"
                    :value="m.modelId"
                >
                  {{ m.modelName }}
                </a-select-option>
              </a-select-opt-group>
            </a-select>
          </div>

          <div class="config-item">
            <div class="config-label">
              <DatabaseOutlined class="config-icon" />
              <span>选择知识库</span>
              <span style="font-size: 12px; color: #999; margin-left: 8px; font-weight: normal;">请在您需要检索知识库中信息时选用</span>
            </div>
            <KbSelector size="large" class="config-select" :disabled="!isKbSupported" />
            <div v-if="!isKbSupported && selectedModel" style="color: #faad14; font-size: 12px; margin-top: 4px;">
              当前模型不支持知识库功能
            </div>
          </div>
        </div>
      </a-card>

      <!-- 输入区域 -->
      <div class="input-section">
        <Sender
            :disabled="loading"
            placeholder="请输入你的第一条问题，开启智能对话之旅…"
            @submit="onSend"
            class="chat-sender"
        />
      </div>

      <!-- 提示区域 -->
      <div class="tips-section">
        <div class="tip-item">💡 支持多轮对话和上下文理解</div>
        <div class="tip-item">🔍 可结合知识库进行精准问答</div>
        <div class="tip-item">⚡ 实时流式输出，响应迅速</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.new-chat-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
  padding: 40px 24px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.content-wrapper {
  width: 100%;
  max-width: 900px;
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.welcome-section {
  text-align: center;
  margin-bottom: 40px;
  color: #333;
}

.welcome-icon {
  font-size: 64px;
  margin-bottom: 20px;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.welcome-title {
  font-size: 36px;
  font-weight: 600;
  margin: 0 0 12px 0;
  color: #333;
}

.welcome-subtitle {
  font-size: 16px;
  opacity: 0.9;
  margin: 0;
}

.config-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
  transition: all 0.3s ease;
}

.config-card:hover {
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.config-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.config-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 500;
  color: #333;
}

.config-icon {
  font-size: 18px;
  color: #1890ff;
}

.config-select {
  /* width: 100%; removed to allow manual width control */
}

.input-section {
  margin-bottom: 24px;
}

.chat-sender {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.chat-sender:hover {
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
}

.tips-section {
  display: flex;
  justify-content: center;
  gap: 20px;
  flex-wrap: wrap;
}

.tip-item {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  padding: 8px 16px;
  border-radius: 20px;
  color: #555;
  font-size: 14px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.tip-item:hover {
  background: rgba(255, 255, 255, 0.95);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.new-chat-container.is-dark .tip-item {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  box-shadow: none;
}

.new-chat-container.is-dark .tip-item:hover {
  background: rgba(255, 255, 255, 0.15);
}



@media (max-width: 768px) {
  .welcome-title {
    font-size: 28px;
  }
  
  .welcome-icon {
    font-size: 48px;
  }
  
  .tips-section {
    flex-direction: column;
    align-items: center;
  }

  .config-select {
    width: 100% !important;
  }
}
</style>

<style>
/* 暗色模式样式 - 非 scoped 以确保优先级和覆盖 */
.new-chat-container.is-dark {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: #e0e0e0;
}

.new-chat-container.is-dark .welcome-section {
  color: white;
}

.new-chat-container.is-dark .welcome-title {
  color: white;
}

.new-chat-container.is-dark .config-card {
  background: rgba(30, 30, 30, 0.95);
}

.new-chat-container.is-dark .config-label {
  color: #e0e0e0;
}

.new-chat-container.is-dark .config-icon {
  color: #a0aeff;
}

.new-chat-container.is-dark .chat-sender {
  background: rgba(30, 30, 30, 0.95);
}

.new-chat-container.is-dark .tip-item {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  box-shadow: none;
}

.new-chat-container.is-dark .tip-item:hover {
  background: rgba(255, 255, 255, 0.15);
}
</style>
