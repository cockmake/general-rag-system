<template>
  <a-card hoverable class="workspace-card">
    <template #title>
      <div class="workspace-title">
        <span>{{ workspace.name }}</span>
        <a-tag v-if="isCurrent" color="green">当前</a-tag>
        <a-tag v-if="isOwner" color="blue">拥有者</a-tag>
      </div>
    </template>

    <template #extra>
      <a-dropdown>
        <a-button type="text" size="small">
          <template #icon>
            <MoreOutlined/>
          </template>
        </a-button>
        <template #overlay>
          <a-menu>
            <a-menu-item v-if="!isCurrent" key="switch" @click="$emit('switch', workspace)">
              <template #icon>
                <SwapOutlined/>
              </template>
              切换到此工作空间
            </a-menu-item>
            <a-menu-item key="members" @click="$emit('view-members', workspace)">
              <template #icon>
                <TeamOutlined/>
              </template>
              查看成员
            </a-menu-item>
            <template v-if="isOwner">
              <a-menu-divider/>
              <a-menu-item key="invite" @click="$emit('invite', workspace)">
                <template #icon>
                  <UserAddOutlined/>
                </template>
                邀请成员
              </a-menu-item>
              <a-menu-item key="edit" @click="$emit('edit', workspace)">
                <template #icon>
                  <EditOutlined/>
                </template>
                编辑
              </a-menu-item>
              <a-menu-divider/>
              <a-menu-item key="delete" danger @click="$emit('delete', workspace)">
                <template #icon>
                  <DeleteOutlined/>
                </template>
                删除
              </a-menu-item>
            </template>
          </a-menu>
        </template>
      </a-dropdown>
    </template>

    <div class="workspace-description">
      {{ workspace.description || '暂无描述' }}
    </div>

    <div class="workspace-info">
      <a-space>
        <span class="info-label">创建时间:</span>
        <span>{{ formatDate(workspace.createdAt) }}</span>
      </a-space>
    </div>
  </a-card>
</template>

<script setup>
import {computed} from 'vue'
import dayjs from 'dayjs'
import {
  MoreOutlined,
  SwapOutlined,
  TeamOutlined,
  UserAddOutlined,
  EditOutlined,
  DeleteOutlined
} from '@ant-design/icons-vue'

const props = defineProps({
  workspace: {
    type: Object,
    required: true
  },
  isCurrent: {
    type: Boolean,
    default: false
  },
  isOwner: {
    type: Boolean,
    default: false
  }
})

defineEmits(['switch', 'edit', 'delete', 'invite', 'view-members'])

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD')
}
</script>

<style scoped>
.workspace-card {
  height: 100%;
}

.workspace-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.workspace-description {
  margin-bottom: 16px;
  color: rgba(0, 0, 0, 0.65);
  min-height: 40px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

body[data-theme='dark'] .workspace-description {
  color: rgba(255, 255, 255, 0.65);
}

.workspace-info {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
  font-size: 12px;
  color: rgba(0, 0, 0, 0.45);
}

body[data-theme='dark'] .workspace-info {
  border-top-color: #424242;
  color: rgba(255, 255, 255, 0.45);
}

.info-label {
  font-weight: 500;
}
</style>
