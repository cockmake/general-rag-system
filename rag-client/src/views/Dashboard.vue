<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { fetchRecentActivities } from '@/api/logApi'
import { fetchDashboardSummary } from '@/api/dashboardApi'
import { fetchLatestNotification } from '@/api/notificationApi'

const userStore = useUserStore()
const activities = ref([])
const loading = ref(false)
const notification = ref(null)
const notificationModalVisible = ref(false)

const stats = ref({
  kbCount: 0,
  documentCount: 0,
  sessionCount: 0,
  todayTokenUsage: 0
})

const fetchStats = async () => {
  try {
    const data = await fetchDashboardSummary()
    if (data) {
      stats.value = data
    }
  } catch (e) {
    console.error('Failed to fetch dashboard stats', e)
  }
}

const fetchActivities = async () => {
  loading.value = true
  try {
    const data = await fetchRecentActivities()
    activities.value = data || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const fetchNotification = async () => {
  try {
    const data = await fetchLatestNotification()
    if (data) {
      notification.value = data
    }
  } catch (e) {
    console.error('Failed to fetch notification', e)
  }
}

const formatTime = (time) => {
  return new Date(time).toLocaleString()
}


onMounted(() => {
  fetchStats()
  fetchActivities()
  fetchNotification()
})

</script>

<template>
  <div class="dashboard-page">
    <!-- Workspace & User -->
    <div class="header">
      <div>
        <h2 class="title">
          👋 欢迎你，{{ userStore.username }}
        </h2>
      </div>
    </div>

    <div v-if="notification" style="margin-bottom: 24px;">
      <a-alert
        message="最新公告"
        type="info"
        show-icon
        closable
      >
        <template #description>
          <div v-if="notification.displayType === 'popup'" style="white-space: pre-wrap">
            <span>{{ notification.content && notification.content.length > 50 ? notification.content.substring(0, 50) + '...' : notification.content }}</span>
            <a-button type="link" @click="notificationModalVisible = true">查看详情</a-button>
          </div>
          <div v-else style="white-space: pre-wrap">
            {{ notification.content }}
          </div>
        </template>
      </a-alert>
      
      <a-modal
        v-model:open="notificationModalVisible"
        title="公告详情"
        :footer="null"
      >
        <div style="white-space: pre-wrap;">{{ notification.content }}</div>
        <div style="margin-top: 16px; color: #999; font-size: 12px; text-align: right;">
          发布于: {{ formatTime(notification.createdAt) }}
        </div>
      </a-modal>
    </div>

    <!-- 核心统计卡片 -->
    <a-row :gutter="16">
      <a-col :span="6">
        <a-card>
          <div class="stat">
            <div class="label">知识库</div>
            <div class="value">{{ stats.kbCount }}</div>
          </div>
        </a-card>
      </a-col>

      <a-col :span="6">
        <a-card>
          <div class="stat">
            <div class="label">文档数</div>
            <div class="value">{{ stats.documentCount }}</div>
          </div>
        </a-card>
      </a-col>

      <a-col :span="6">
        <a-card>
          <div class="stat">
            <div class="label">对话数</div>
            <div class="value">{{ stats.sessionCount }}</div>
          </div>
        </a-card>
      </a-col>

      <a-col :span="6">
        <a-card>
          <div class="stat">
            <div class="label">今日消耗Token</div>
            <div class="value">{{ stats.todayTokenUsage }}</div>
          </div>
        </a-card>
      </a-col>

    </a-row>

    <a-divider />

    <!-- 最近活动 -->
    <a-card title="最近活动" :loading="loading">
      <a-empty v-if="activities.length === 0" description="暂无活动记录" />
      <a-timeline v-else>
        <a-timeline-item v-for="item in activities" :key="item.id">
          <span style="color: #666; font-size: 12px; margin-right: 8px;">{{ formatTime(item.createdAt) }}</span>
          <span>{{ item.displayMessage || item.action }}</span>
          <span v-if="item.status === 'FAIL'" style="color: red; margin-left: 8px;">(失败: {{ item.errorMessage }})</span>
        </a-timeline-item>
      </a-timeline>
    </a-card>
  </div>
</template>

<style scoped>
.dashboard-page {
  padding: 24px;
}

.header {
  margin-bottom: 24px;
}

.title {
  margin-bottom: 4px;
}

.subtitle {
  color: #666;
  margin: 0;
}

.stat {
  text-align: center;
}

.stat .label {
  color: #888;
  font-size: 14px;
}

.stat .value {
  font-size: 28px;
  font-weight: bold;
  margin-top: 8px;
}
</style>
