<template>
  <div class="workspace-management">
    <a-card title="工作空间管理" :bordered="false">
      <template #extra>
        <a-button type="primary" @click="showCreateModal">
          <template #icon>
            <PlusOutlined/>
          </template>
          创建工作空间
        </a-button>
      </template>

      <a-tabs v-model:activeKey="activeTab">
        <!-- 拥有的工作空间 -->
        <a-tab-pane key="owned" tab="我拥有的">
          <a-list
              :data-source="ownedWorkspaces"
              :loading="loading"
              :grid="{ gutter: 16, xs: 1, sm: 2, md: 2, lg: 3, xl: 3, xxl: 4 }"
          >
            <template #renderItem="{ item }">
              <a-list-item>
                <WorkspaceCard
                    :workspace="item"
                    :is-current="currentWorkspace?.id === item.id"
                    :is-owner="true"
                    @switch="handleSwitch"
                    @edit="handleEdit"
                    @delete="handleDelete"
                    @invite="handleInvite"
                    @view-members="handleViewMembers"
                />
              </a-list-item>
            </template>
          </a-list>
        </a-tab-pane>

        <!-- 加入的工作空间 -->
        <a-tab-pane key="member" tab="我加入的">
          <a-list
              :data-source="memberWorkspaces"
              :loading="loading"
              :grid="{ gutter: 16, xs: 1, sm: 2, md: 2, lg: 3, xl: 3, xxl: 4 }"
          >
            <template #renderItem="{ item }">
              <a-list-item>
                <WorkspaceCard
                    :workspace="item"
                    :is-current="currentWorkspace?.id === item.id"
                    :is-owner="false"
                    @switch="handleSwitch"
                    @view-members="handleViewMembers"
                />
              </a-list-item>
            </template>
          </a-list>
        </a-tab-pane>
      </a-tabs>
    </a-card>

    <!-- 创建/编辑工作空间对话框 -->
    <a-modal
        v-model:open="createModalVisible"
        :title="isEditing ? '编辑工作空间' : '创建工作空间'"
        :confirm-loading="submitting"
        @ok="handleSubmit"
    >
      <a-form :model="formData" :label-col="{ span: 6 }" :wrapper-col="{ span: 18 }">
        <a-form-item label="工作空间名称" required>
          <a-input v-model:value="formData.name" placeholder="请输入工作空间名称" :maxlength="100"/>
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea
              v-model:value="formData.description"
              placeholder="请输入工作空间描述"
              :rows="4"
              :maxlength="500"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 邀请用户对话框 -->
    <a-modal
        v-model:open="inviteModalVisible"
        title="邀请用户"
        :confirm-loading="submitting"
        @ok="handleInviteSubmit"
    >
      <a-form :model="inviteFormData" :label-col="{ span: 6 }" :wrapper-col="{ span: 18 }">
        <a-form-item label="用户名或邮箱" required>
          <a-input v-model:value="inviteFormData.userIdentifier" placeholder="请输入用户名或邮箱"/>
        </a-form-item>
        <a-alert 
          message="邀请的用户将自动成为工作空间成员" 
          type="info" 
          show-icon 
          style="margin-top: 12px;"
        />
      </a-form>
    </a-modal>

    <!-- 成员列表对话框 -->
    <a-modal
        v-model:open="membersModalVisible"
        title="工作空间成员"
        :footer="null"
        width="800px"
    >
      <a-table
          :columns="memberColumns"
          :data-source="members"
          :loading="loadingMembers"
          :pagination="false"
          row-key="id"
          :scroll="{ x: 600 }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'role'">
            <a-tag :color="record.role === 'owner' ? 'blue' : 'green'">
              {{ record.role === 'owner' ? '拥有者' : '成员' }}
            </a-tag>
          </template>
          <template v-if="column.key === 'joinedAt'">
            {{ formatDate(record.joinedAt) }}
          </template>
          <template v-if="column.key === 'action'">
            <a-button
                v-if="canRemoveMember(record)"
                type="link"
                danger
                @click="handleRemoveMember(record)">
              移除
            </a-button>
          </template>
        </template>
      </a-table>
    </a-modal>
  </div>
</template>

<script setup>
import {ref, computed, onMounted} from 'vue'
import {message, Modal} from 'ant-design-vue'
import {PlusOutlined} from '@ant-design/icons-vue'
import dayjs from 'dayjs'
import workspaceApi from '@/api/workspaceApi.js'
import WorkspaceCard from './WorkspaceCard.vue'

const activeTab = ref('owned')
const loading = ref(false)
const submitting = ref(false)
const createModalVisible = ref(false)
const inviteModalVisible = ref(false)
const membersModalVisible = ref(false)
const loadingMembers = ref(false)
const isEditing = ref(false)

const ownedWorkspaces = ref([])
const memberWorkspaces = ref([])
const currentWorkspace = ref(null)  // 用户当前选中的工作空间
const currentViewingWorkspace = ref(null)  // 当前正在查看/操作的工作空间
const members = ref([])

const formData = ref({
  id: null,
  name: '',
  description: ''
})

const inviteFormData = ref({
  workspaceId: null,
  userIdentifier: ''
  // 移除 role 字段，后端会自动设置为 member
})

const memberColumns = [
  {title: '用户名', dataIndex: 'username', key: 'username'},
  {title: '邮箱', dataIndex: 'email', key: 'email'},
  {title: '角色', dataIndex: 'role', key: 'role'},
  {title: '加入时间', dataIndex: 'joinedAt', key: 'joinedAt'},
  {title: '操作', key: 'action', width: 100}
]

const canRemoveMember = computed(() => (member) => {
  // 不能移除拥有者角色的成员
  return member.role !== 'owner'
})

const loadWorkspaces = async () => {
  loading.value = true
  try {
    const data = await workspaceApi.getWorkspaces()
    ownedWorkspaces.value = data.owned || []
    memberWorkspaces.value = data.member || []
    currentWorkspace.value = data.current
  } catch (error) {
    console.error('加载工作空间失败:', error)
  } finally {
    loading.value = false
  }
}

const showCreateModal = () => {
  isEditing.value = false
  formData.value = {id: null, name: '', description: ''}
  createModalVisible.value = true
}

const handleEdit = (workspace) => {
  isEditing.value = true
  formData.value = {...workspace}
  createModalVisible.value = true
}

const handleSubmit = async () => {
  if (!formData.value.name?.trim()) {
    message.warning('请输入工作空间名称')
    return
  }

  submitting.value = true
  try {
    if (isEditing.value) {
      await workspaceApi.updateWorkspace(formData.value.id, {
        name: formData.value.name,
        description: formData.value.description
      })
    } else {
      await workspaceApi.createWorkspace({
        name: formData.value.name,
        description: formData.value.description
      })
    }
    createModalVisible.value = false
    await loadWorkspaces()
  } catch (error) {
    console.error('操作失败:', error)
  } finally {
    submitting.value = false
  }
}

const handleSwitch = async (workspace) => {
  try {
    await workspaceApi.switchWorkspace(workspace.id)
    // 刷新页面以应用新的工作空间
    window.location.reload()
  } catch (error) {
    console.error('切换工作空间失败:', error)
  }
}

const handleDelete = (workspace) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除工作空间"${workspace.name}"吗？此操作不可恢复。`,
    okText: '确定',
    okType: 'danger',
    cancelText: '取消',
    async onOk() {
      try {
        await workspaceApi.deleteWorkspace(workspace.id)
        await loadWorkspaces()
      } catch (error) {
        console.error('删除工作空间失败:', error)
      }
    }
  })
}

const handleInvite = (workspace) => {
  currentViewingWorkspace.value = workspace  // 记录当前操作的工作空间
  inviteFormData.value = {
    workspaceId: workspace.id,
    userIdentifier: ''
  }
  inviteModalVisible.value = true
}

const handleInviteSubmit = async () => {
  if (!inviteFormData.value.userIdentifier?.trim()) {
    message.warning('请输入用户名或邮箱')
    return
  }

  submitting.value = true
  try {
    await workspaceApi.inviteUser(inviteFormData.value)
    inviteModalVisible.value = false
  } catch (error) {
    console.error('邀请用户失败:', error)
  } finally {
    submitting.value = false
  }
}

const handleViewMembers = async (workspace) => {
  currentViewingWorkspace.value = workspace  // 记录当前查看的工作空间
  membersModalVisible.value = true
  loadingMembers.value = true
  
  try {
    members.value = await workspaceApi.getMembers(workspace.id)
  } catch (error) {
    console.error('加载成员列表失败:', error)
  } finally {
    loadingMembers.value = false
  }
}

const handleRemoveMember = (member) => {
  Modal.confirm({
    title: '确认移除',
    content: `确定要移除成员"${member.username}"吗？`,
    okText: '确定',
    okType: 'danger',
    cancelText: '取消',
    async onOk() {
      try {
        // 使用当前查看的工作空间 ID
        await workspaceApi.removeMember(currentViewingWorkspace.value.id, member.userId)
        // 刷新成员列表
        await handleViewMembers(currentViewingWorkspace.value)
      } catch (error) {
        console.error('移除成员失败:', error)
      }
    }
  })
}

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

onMounted(() => {
  loadWorkspaces()
})
</script>

<style scoped>
.workspace-management {
  padding: 24px;
}
</style>
