<script setup>
import {ref, onMounted, computed, h, watch, onUnmounted} from 'vue'
import {useRouter, useRoute} from 'vue-router'
import {message, Button, Typography} from 'ant-design-vue'
import {Conversations} from 'ant-design-x-vue'
import {CommentOutlined, ClockCircleOutlined, DeleteOutlined} from '@ant-design/icons-vue'
import {deleteSession, fetchSessions} from '@/api/chatApi'
import {events} from '@/events.js';

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const groups = ref([])
const cursor = ref(null)
const hasMore = ref(true)
const activeKey = ref(route.params.sessionId)

const loadData = async () => {
  if (loading.value || !hasMore.value) return
  loading.value = true

  const res = await fetchSessions({
    lastActiveAt: cursor.value?.lastActiveAt,
    lastId: cursor.value?.lastId,
    pageSize: 20
  })

  groups.value.push(...(res.groups || []))
  cursor.value = res.nextCursor
  hasMore.value = res.hasMore
  loading.value = false
}

const conversationItems = computed(() =>
    groups.value.flatMap(g =>
        g.items.map(i => ({
          key: i.id.toString(),
          label: i.title,
          timestamp: i.timestamp,
          group: g.group,
          icon: h(CommentOutlined),
        }))
    )
)
const menu = (conversation) => ({
  items: [
    {
      label: '删除会话',
      key: 'delete',
      icon: h(DeleteOutlined),
      danger: true,
    },
  ],
  onClick: (menuInfo) => {
    if (menuInfo.key === 'delete') {
      deleteSession(conversation.key).then(() => {
        const group = groups.value.find(g => g.group === conversation.group)
        if (group) {
          group.items = group.items.filter(i => i.id.toString() !== conversation.key)
          // 如果该组没有更多会话，移除该组
          if (group.items.length === 0) {
            groups.value = groups.value.filter(g => g.group !== conversation.group)
          }
        }
        if (activeKey.value === conversation.key) {
          router.push('/chat/new')
        }
      })
    }
  },
});

const groupable = {
  sort(a, b) {
    const order = {TODAY: 0, YESTERDAY: 1, EARLIER: 2}
    return (order[a] ?? 99) - (order[b] ?? 99)
  },
  title: (group, {components: {GroupTitle}}) => {
    const map = {
      TODAY: '今天',
      YESTERDAY: '昨天',
      EARLIER: '更早'
    }
    return h(GroupTitle, null, () => map[group] || group)
  }
}

const handleActiveChange = (key) => {
  router.push(`/chat/${key}`)
}

watch(
    () => route.params.sessionId,
    (val) => {
      activeKey.value = val
    }
)

onMounted(() => {
  loadData()
  events.on('sessionListRefresh', () => {
    // ⭐ 核心逻辑
    groups.value = []
    cursor.value = null
    hasMore.value = true
    loadData()
  })
  events.on('sessionTitleUpdated', ({sessionId, title}) => {
    for (const g of groups.value) {
      const item = g.items.find(i => i.id === sessionId)
      if (item) {
        item.title = title
        break
      }
    }
  })
})
onUnmounted(() => {
  events.off('sessionListRefresh')
  events.off('sessionTitleUpdated')
})
</script>

<template>
  <div style='display: flex; flex-direction: column; height: 100%;'>
    <div style='flex: 1; overflow-y: auto;'>
      <Conversations
          :items='conversationItems'
          :activeKey='activeKey'
          :menu='menu'
          :groupable='groupable'
          :onActiveChange='handleActiveChange'
      />
      <Button
          block
          :loading='loading'
          @click='loadData'>
        <ClockCircleOutlined/>
        查看更多历史
      </Button>
    </div>
  </div>
</template>

<style scoped>
:deep(.ant-conversations) {
  .ant-conversations-group-title {
    padding-inline-start: 0 !important;
  }

  .ant-conversations-item {
    padding-inline-start: 5px !important;
  }
}
</style>
