<script setup>
import {onMounted, ref} from 'vue';
import {useRouter} from 'vue-router';
import {message, Modal, theme} from 'ant-design-vue';
import {createKb, deleteKb, fetchAvailableKbs} from "@/api/kbApi.js";

const {useToken} = theme;
const {token} = useToken();
const router = useRouter();

const isModalVisible = ref(false);
const formState = ref({
  name: '',
  description: '',
  visibility: 'private'
});

// 修改：将单一列表改为符合后端返回结构的 Map 对象
const kbMap = ref({
  private: [],      // 个人/我创建的
  shared: [],  // 空间共享的
  public: [],      // 公共的
  invited: []      // 被邀请访问的
});

const isLoading = ref(false);

// 封装加载数据的方法，便于复用
const loadData = async () => {
  isLoading.value = true;
  try {
    const data = await fetchAvailableKbs();
    console.log(data)
    // 确保后端返回的是 Map 结构，如果后端直接返回 data，则直接赋值
    // 如果后端包裹在 result.data 中，请根据实际情况调整
    if (data) {
      kbMap.value = {
        private: data.private || [],
        shared: data.shared || [],
        public: data.public || [],
        invited: data.invited || []
      };
    }
  } catch (e) {
    message.error('加载知识库列表失败');
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  loadData();
});

const handleCreate = async () => {
  if (!formState.value.name) return message.error('请输入名称');
  try {
    await createKb(formState.value);
    message.success('创建成功');
    isModalVisible.value = false;
    // 创建成功后刷新列表
    loadData();
    // 重置表单
    formState.value = {name: '', description: '', visibility: 'private'};
  } catch (e) {
    // 错误已由拦截器处理
  }
};

const goToDetail = (id) => {
  router.push(`/kb/${id}`);
};

const handleDelete = (id) => {
  Modal.confirm({
    title: '确认删除?',
    content: '删除后无法恢复，且会删除关联的所有文档。',
    okText: '确认删除',
    okType: 'danger',
    cancelText: '取消',
    onOk: async () => {
      try {
        await deleteKb(id);
        message.success('已删除');
        loadData(); // 删除成功后刷新列表
      } catch (e) {
        // 错误已拦截
      }
    }
  });
};
</script>

<template>
  <div style="padding: 24px">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
      <h2 :style="{ color: token.colorTextHeading }">📚 知识库管理</h2>
      <a-button type="primary" @click="isModalVisible = true">新建知识库</a-button>
    </div>

    <div class="kb-section">
      <h3><span role="img" aria-label="user">👤</span> 我创建的知识库</h3>
      <a-list :grid="{ gutter: 16, column: 4 }" :data-source="kbMap.private" :loading="isLoading">
        <template #renderItem="{ item }">
          <a-list-item>
            <a-card hoverable @click="goToDetail(item.id)" class="kb-card">
              <template #actions>
                <a-button type="text" danger @click.stop="handleDelete(item.id)">删除</a-button>
              </template>
              <a-card-meta :title="item.name" :description="item.description || '暂无描述'">
                <template #avatar>
                  <a-avatar style="background-color: #1890ff">私</a-avatar>
                </template>
              </a-card-meta>
            </a-card>
          </a-list-item>
        </template>
      </a-list>
    </div>

    <a-divider/>

    <div class="kb-section">
      <h3><span role="img" aria-label="team">🏢</span> 工作空间共享</h3>
      <a-list :grid="{ gutter: 16, column: 4 }" :data-source="kbMap.shared" :loading="isLoading">
        <template #renderItem="{ item }">
          <a-list-item>
            <a-card hoverable @click="goToDetail(item.id)" class="kb-card">
              <a-card-meta :title="item.name" :description="item.description || '暂无描述'">
                <template #avatar>
                  <a-avatar style="background-color: #52c41a">共</a-avatar>
                </template>
              </a-card-meta>
            </a-card>
          </a-list-item>
        </template>
      </a-list>
    </div>


    <a-divider/>

    <div class="kb-section">
      <h3><span role="img" aria-label="globe">🌍</span> 公共知识库</h3>
      <a-list :grid="{ gutter: 16, column: 4 }" :data-source="kbMap.public" :loading="isLoading">
        <template #renderItem="{ item }">
          <a-list-item>
            <a-card hoverable @click="goToDetail(item.id)" class="kb-card">
              <a-card-meta :title="item.name" :description="item.description || '暂无描述'">
                <template #avatar>
                  <a-avatar style="background-color: #faad14">公</a-avatar>
                </template>
              </a-card-meta>
            </a-card>
          </a-list-item>
        </template>
      </a-list>
    </div>

    <a-divider/>

    <div class="kb-section">
      <h3><span role="img" aria-label="invited">📧</span> 受邀访问的知识库</h3>
      <a-list :grid="{ gutter: 16, column: 4 }" :data-source="kbMap.invited" :loading="isLoading">
        <template #renderItem="{ item }">
          <a-list-item>
            <a-card hoverable @click="goToDetail(item.id)" class="kb-card">
              <a-card-meta :title="item.name" :description="item.description || '暂无描述'">
                <template #avatar>
                  <a-avatar style="background-color: #722ed1">邀</a-avatar>
                </template>
              </a-card-meta>
            </a-card>
          </a-list-item>
        </template>
      </a-list>
    </div>

    <a-modal v-model:visible="isModalVisible" title="新建知识库" @ok="handleCreate" style="min-width: 380px">
      <a-form layout="vertical">
        <a-form-item label="名称" required>
          <a-input v-model:value="formState.name" placeholder="请输入知识库名称"/>
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea v-model:value="formState.description" placeholder="请输入简要描述"/>
        </a-form-item>
        <a-form-item label="可见性">
          <a-radio-group v-model:value="formState.visibility" option-type="button">
            <a-radio value="private">私有 (仅自己可见)</a-radio>
            <a-radio value="shared">共享 (同工作空间可见)</a-radio>
            <a-radio value="public">公开 (所有人可见)</a-radio>
          </a-radio-group>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<style scoped>
.kb-section {
  margin-bottom: 24px;
}

.kb-section h3 {
  margin-bottom: 16px;
  font-weight: 600;
  color: v-bind('token.colorTextHeading');
}

.kb-card {
  /* 统一卡片高度，防止描述长短不一导致不对齐 */
  height: 100%;
}
</style>