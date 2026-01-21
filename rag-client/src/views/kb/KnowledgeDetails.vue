<script setup>
import {onMounted, ref, computed, watch} from "vue";
import {onUnmounted} from "vue";
import VuePdfEmbed from 'vue-pdf-embed';
import 'vue-pdf-embed/dist/styles/annotationLayer.css';
import 'vue-pdf-embed/dist/styles/textLayer.css';
import md from "@/utils/markdown.js";
import {useRoute, useRouter} from "vue-router";
import {message} from "ant-design-vue";
import { LoadingOutlined, ArrowLeftOutlined } from '@ant-design/icons-vue';
import {deleteDocument, previewDocument, listDocuments, uploadDocument, renameDocument, listChunks, inviteUserToKb, getInvitedUsers, removeInvitedUser, fetchAvailableKbs, updateKb} from "@/api/kbApi.js";
import { useUserStore } from "@/stores/user";

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const kbId = route.params.kbId;
const fileList = ref([]);
const uploading = ref(false);
const currentKb = ref(null);

const goBack = () => {
  router.push('/kb');
};

// 判断是否是拥有者
const isOwner = computed(() => {
  return currentKb.value && currentKb.value.ownerUserId === userStore.userId;
});

// Settings related refs
const settingsModalVisible = ref(false);
const settingsForm = ref({
  name: '',
  description: '',
  systemPrompt: ''
});
const settingsSubmitting = ref(false);

const openSettingsModal = () => {
  if (currentKb.value) {
    settingsForm.value = {
      name: currentKb.value.name,
      description: currentKb.value.description,
      systemPrompt: currentKb.value.systemPrompt || ''
    };
    settingsModalVisible.value = true;
  }
};

const handleSettingsSubmit = async () => {
  settingsSubmitting.value = true;
  try {
    await updateKb(kbId, settingsForm.value);
    message.success('更新成功');
    settingsModalVisible.value = false;
    fetchKbInfo(); // Refresh info
  } catch (e) {
    console.error('Update failed', e);
  } finally {
    settingsSubmitting.value = false;
  }
};

// 判断是否是私有知识库且是拥有者
const canInvite = computed(() => {
  return currentKb.value && currentKb.value.visibility === 'private' && isOwner.value;
});

// Preview related refs
const previewVisible = ref(false);
const previewContent = ref('');
const previewType = ref('text');
const previewTitle = ref('预览');
const pdfPage = ref(1);
const pdfPageCount = ref(0);

// Rename related refs
const renameModalVisible = ref(false);
const currentRenameRecord = ref(null);
const newFileName = ref('');

// Invite related refs
const inviteModalVisible = ref(false);
const inviteFormData = ref({
  kbId: kbId,
  userIdentifier: ''
});
const inviteSubmitting = ref(false);

// Invited users related refs
const invitedUsersModalVisible = ref(false);
const invitedUsers = ref([]);
const loadingInvitedUsers = ref(false);

// Upload progress related refs
const uploadProgressModalVisible = ref(false);
const uploadProgressList = ref([]);
const activeUploadsCount = ref(0);

// Download/Preview progress related refs
const downloadProgress = ref({
  visible: false,
  percent: 0,
  title: ''
});

let progressTimer = null;

const startSimulatedProgress = () => {
  downloadProgress.value.percent = 0;
  if (progressTimer) clearInterval(progressTimer);
  
  progressTimer = setInterval(() => {
    if (downloadProgress.value.percent < 99) {
      // Slow down as it gets higher
      // Start fast, then slow down
      let increment = 5;
      if (downloadProgress.value.percent > 50) increment = 2;
      if (downloadProgress.value.percent > 80) increment = 1;
      if (downloadProgress.value.percent > 95) {
         // Very slow at the end, maybe stop at 99
         if (Math.random() > 0.8) increment = 1;
         else increment = 0;
      }
      
      downloadProgress.value.percent = Math.min(99, downloadProgress.value.percent + increment);
    }
  }, 200);
};

const finishSimulatedProgress = () => {
  if (progressTimer) clearInterval(progressTimer);
  downloadProgress.value.percent = 100;
  // Delay slightly to show 100%
  setTimeout(() => {
      downloadProgress.value.visible = false;
  }, 500);
};

watch(uploadProgressModalVisible, (val) => {
  if (!val && activeUploadsCount.value === 0) {
    uploadProgressList.value = [];
  }
});

const systemPromptPlaceholder = `你是一个专业的AI助手。基于提供的文档和对话历史回答用户问题。

要求：
1. 提供的文档中的信息可供参考
2. 如果文档不足以完整回答，结合对话历史和已有知识回答或直接明确说明
3. 保持对话连贯，考虑历史上下文
4. 用清晰、简洁的语言回答
5. 文件为切片信息，编排可能较乱，你需要提取相关信息`;

const acceptExtensions = ".md,.txt,.pdf,.json,.py,.java,.js,.ts,.vue,.html,.xml,.yml,.sh,.rb,.css,.scss,.jpg,.jpeg,.png,.gif,.bmp,.webp";

const invitedUsersColumns = [
  {title: '用户名', dataIndex: 'username', key: 'username'},
  {title: '邮箱', dataIndex: 'email', key: 'email'},
  {title: '邀请人', dataIndex: 'grantedByUsername', key: 'grantedByUsername'},
  {title: '邀请时间', dataIndex: 'grantedAt', key: 'grantedAt'},
  {title: '操作', key: 'action', width: 100}
];

const columns = [
  {title: '文件名', dataIndex: 'fileName', key: 'fileName'},
  {title: '大小', dataIndex: 'fileSize', key: 'fileSize'},
  {title: '状态', dataIndex: 'status', key: 'status'}, // processing, ready, failed
  {title: '上传时间', dataIndex: 'createdAt', key: 'createdAt'},
  {title: '操作', key: 'action'},
];


const fetchDocuments = async () => {
  fileList.value = await listDocuments(kbId).then();
};

// 获取当前知识库信息
const fetchKbInfo = async () => {
  try {
    const data = await fetchAvailableKbs();
    // 在所有分类中查找当前知识库
    const allKbs = [
      ...(data.private || []),
      ...(data.shared || []),
      ...(data.public || []),
      ...(data.invited || [])
    ];
    currentKb.value = allKbs.find(kb => kb.id == kbId);
  } catch (e) {
    console.error('Failed to fetch KB info', e);
  }
};

// 1. 上传逻辑
const beforeUpload = (file) => {
  const extension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
  const allowed = acceptExtensions.split(',');
  if (!allowed.includes(extension)) {
    message.error(`不支持的文件类型: ${file.name}`);
    return false; // 阻止上传
  }
  return true;
};

const customRequest = async (options) => {
  const { file, onSuccess, onError } = options;
  
  // Initialize file in progress list
  const fileItem = {
    uid: file.uid,
    name: file.name,
    status: 'uploading',
    percent: 0,
    error: null
  };
  
  // Add to list
  uploadProgressList.value.push(fileItem);
  uploadProgressModalVisible.value = true;
  activeUploadsCount.value++;
  uploading.value = true;

  const formData = new FormData();
  formData.append('files', file);

  try {
    await uploadDocument(kbId, formData, {
      onUploadProgress: (progressEvent) => {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        const item = uploadProgressList.value.find(item => item.uid === file.uid);
        if (item) {
          item.percent = percent;
        }
      }
    });
    
    // Success
    const item = uploadProgressList.value.find(item => item.uid === file.uid);
    if (item) {
      item.status = 'done';
      item.percent = 100;
    }
    message.success(`${file.name} 上传成功`);
    onSuccess(null, file);
    fetchDocuments();
  } catch (err) {
    // Error
    const item = uploadProgressList.value.find(item => item.uid === file.uid);
    if (item) {
      item.status = 'error';
      item.error = err.message || '上传失败';
    }
    onError(err);
  } finally {
    activeUploadsCount.value--;
    if (activeUploadsCount.value === 0) {
      uploading.value = false;
    }
  }
};

// 2. 预览逻辑
const handlePreview = async (record) => {
  downloadProgress.value = { visible: true, percent: 0, title: '正在加载预览...' };
  startSimulatedProgress();
  try {
    const blob = await previewDocument(kbId, record.id);
    finishSimulatedProgress();

    const fileName = record.fileName ? record.fileName.toLowerCase() : '';
    previewTitle.value = record.fileName || '文件预览';

    if (fileName.endsWith('.pdf')) {
      previewType.value = 'pdf';
      previewContent.value = window.URL.createObjectURL(blob);
      pdfPage.value = 1;
      pdfPageCount.value = 0;
    } else if (fileName.endsWith('.md')) {
      previewType.value = 'markdown';
      previewContent.value = await blob.text();
    } else if (fileName.match(/\.(jpeg|jpg|png|gif|bmp|webp)$/)) {
        previewType.value = 'image';
        previewContent.value = window.URL.createObjectURL(blob);
    } else {
      previewType.value = 'text';
      previewContent.value = await blob.text();
    }
    previewVisible.value = true;
  } catch (e) {
    console.error('Preview failed', e);
    message.error('预览失败');
    downloadProgress.value.visible = false;
    if (progressTimer) clearInterval(progressTimer);
  }
};

const handlePreviewCancel = () => {
    previewVisible.value = false;
    // Optional cleanup
    if (['pdf', 'image'].includes(previewType.value)) {
        URL.revokeObjectURL(previewContent.value);
    }
    previewContent.value = '';
};

const handlePdfLoaded = (doc) => {
  pdfPageCount.value = doc.numPages;
};

const changePage = (delta) => {
  const newPage = pdfPage.value + delta;
  if (newPage >= 1 && newPage <= pdfPageCount.value) {
    pdfPage.value = newPage;
  }
};

// 3. 删除逻辑
const handleDelete = async (record) => {
  await deleteDocument(kbId, record.id);
  message.success('已删除');
  fetchDocuments();
};

// 4. 重命名逻辑
const openRenameModal = (record) => {
  currentRenameRecord.value = record;
  newFileName.value = record.fileName;
  renameModalVisible.value = true;
};

const handleRename = async () => {
  if (!newFileName.value || !newFileName.value.trim()) {
    message.warning('请输入文件名');
    return;
  }
  try {
    await renameDocument(kbId, currentRenameRecord.value.id, newFileName.value);
    message.success('重命名成功');
    renameModalVisible.value = false;
    fetchDocuments();
  } catch (e) {
    console.error('Rename failed', e);
  }
};

// 5. 下载逻辑
const handleDownload = async (record) => {
  downloadProgress.value = { visible: true, percent: 0, title: '正在准备下载...' };
  startSimulatedProgress();
  try {
    const blob = await previewDocument(kbId, record.id);
    finishSimulatedProgress();

    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = record.fileName || 'download';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    message.success('开始下载');
  } catch (e) {
    console.error('Download failed', e);
    message.error('下载失败');
    downloadProgress.value.visible = false;
    if (progressTimer) clearInterval(progressTimer);
  }
};

// 6. 切片预览逻辑
const chunksDrawerVisible = ref(false);
const chunksList = ref([]);
const chunksLoading = ref(false);
const currentDocId = ref(null);
const currentPage = ref(1);
const pageSize = ref(10);
const hasMoreChunks = ref(true);

const handlePreviewChunks = (record) => {
  currentDocId.value = record.id;
  currentPage.value = 1;
  chunksList.value = [];
  hasMoreChunks.value = true;
  chunksDrawerVisible.value = true;
  fetchChunks();
};

const fetchChunks = async () => {
  if (!currentDocId.value) return;
  chunksLoading.value = true;
  try {
    const res = await listChunks(kbId, currentDocId.value, currentPage.value, pageSize.value);
    if (res && res.records) {
      chunksList.value.push(...res.records);
      // Determine if there are more chunks
      if (res.records.length < pageSize.value || chunksList.value.length >= res.total) {
        hasMoreChunks.value = false;
      }
    } else {
      hasMoreChunks.value = false;
    }
  } catch (e) {
    console.error("Failed to load chunks", e);
  } finally {
    chunksLoading.value = false;
  }
};

const loadMoreChunks = () => {
  currentPage.value++;
  fetchChunks();
};

const closeChunksDrawer = () => {
  chunksDrawerVisible.value = false;
  chunksList.value = [];
};

// 7. 邀请用户逻辑
const showInviteModal = () => {
  inviteFormData.value.userIdentifier = '';
  inviteModalVisible.value = true;
};

const handleInviteSubmit = async () => {
  if (!inviteFormData.value.userIdentifier || !inviteFormData.value.userIdentifier.trim()) {
    message.warning('请输入用户名或邮箱');
    return;
  }
  
  inviteSubmitting.value = true;
  try {
    await inviteUserToKb(kbId, inviteFormData.value);
    message.success('邀请成功');
    inviteModalVisible.value = false;
  } catch (e) {
    console.error('Invite failed', e);
  } finally {
    inviteSubmitting.value = false;
  }
};

// 8. 查看被邀请用户列表
const showInvitedUsersModal = async () => {
  invitedUsersModalVisible.value = true;
  loadingInvitedUsers.value = true;
  
  try {
    invitedUsers.value = await getInvitedUsers(kbId);
  } catch (e) {
    console.error('Failed to load invited users', e);
  } finally {
    loadingInvitedUsers.value = false;
  }
};

// 9. 移除被邀请用户
const handleRemoveInvitedUser = async (record) => {
  try {
    await removeInvitedUser(kbId, record.userId);
    message.success('已移除');
    // 刷新列表
    showInvitedUsersModal();
  } catch (e) {
    console.error('Remove failed', e);
  }
};

const isMobile = ref(false)

const checkIsMobile = () => {
  isMobile.value = window.innerWidth <= 768
}

onMounted(() => {
  checkIsMobile()
  window.addEventListener('resize', checkIsMobile)
  fetchKbInfo();
  fetchDocuments();
});

onUnmounted(() => {
  window.removeEventListener('resize', checkIsMobile)
})
</script>

<template>
  <div style="padding: 24px">
    <div class="kb-header">
      <div class="kb-title-container">
        <a-button @click="goBack" type="text" shape="circle">
          <template #icon><arrow-left-outlined /></template>
        </a-button>
        <h2 class="kb-title">📄 文档管理 - {{ currentKb ? currentKb.name : '' }}</h2>
      </div>
      <div class="kb-actions">
        <a-button v-if="isOwner" @click="openSettingsModal">
          <span v-if="!isMobile">⚙️ 设置</span>
          <span v-else>⚙️</span>
        </a-button>
        <a-button v-if="canInvite" @click="showInvitedUsersModal">
          <span v-if="!isMobile">👥 查看被邀请用户</span>
          <span v-else>👥</span>
        </a-button>
        <a-button v-if="canInvite" @click="showInviteModal">
          <span v-if="!isMobile">📧 邀请用户</span>
          <span v-else>📧</span>
        </a-button>
        <a-upload
            :customRequest="customRequest"
            :showUploadList="false"
            :accept="acceptExtensions"
            :before-upload="beforeUpload"
            multiple>
          <a-button type="primary" :loading="uploading">
            <span v-if="!isMobile">⬆️ 上传文档</span>
            <span v-else>⬆️</span>
          </a-button>
        </a-upload>
      </div>
    </div>

    <a-table :columns="columns" :data-source="fileList" row-key="id" :scroll="{ x: 800 }">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'fileSize'">
          {{ (record.fileSize / (1024 * 1024)).toFixed(2) }} MB
        </template>
        <template v-if="column.key === 'status'">
          <a-tag v-if="record.status === 'processing'" color="blue">
            <loading-outlined />
            向量化中
          </a-tag>
          <a-tag v-else-if="record.status === 'ready'" color="green">完成</a-tag>
          <a-tag v-else-if="record.status === 'failed'" color="red">失败</a-tag>
          <a-tag v-else color="default">{{ record.status }}</a-tag>
        </template>
        <template v-if="column.key === 'action'">
          <a-button type="link" size="small" @click="handlePreview(record)">预览</a-button>
          <a-divider type="vertical"/>
          <a-button type="link" size="small" @click="handleDownload(record)">下载</a-button>
          <a-divider type="vertical"/>
          <a-button type="link" size="small" @click="handlePreviewChunks(record)">预览切片</a-button>
          <a-divider type="vertical"/>
          <a-button type="link" size="small" @click="openRenameModal(record)">重命名</a-button>
          <a-divider type="vertical"/>
          <a-popconfirm
            title="确定要删除这个文件吗？"
            ok-text="确定"
            cancel-text="取消"
            @confirm="handleDelete(record)"
          >
            <a-button type="link" danger size="small">删除</a-button>
          </a-popconfirm>
        </template>
      </template>
    </a-table>

    <a-modal
      v-model:visible="renameModalVisible"
      title="重命名文件"
      @ok="handleRename"
    >
      <a-input v-model:value="newFileName" placeholder="请输入新文件名" />
    </a-modal>

    <!-- 设置对话框 -->
    <a-modal
        v-model:visible="settingsModalVisible"
        title="知识库设置"
        :confirm-loading="settingsSubmitting"
        @ok="handleSettingsSubmit"
        width="600px"
    >
      <a-form :model="settingsForm" layout="vertical">
        <a-form-item label="知识库名称" required>
          <a-input v-model:value="settingsForm.name" placeholder="请输入知识库名称"/>
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea v-model:value="settingsForm.description" placeholder="请输入描述" :rows="2"/>
        </a-form-item>
        <a-form-item label="系统提示词">
            <template #help>
                设置该知识库在对话时的默认系统提示词，用于控制 AI 的回答风格和行为。
            </template>
          <a-textarea v-model:value="settingsForm.systemPrompt" :placeholder="systemPromptPlaceholder" :rows="6"/>
        </a-form-item>
      </a-form>
    </a-modal>

    <a-modal
      v-model:visible="previewVisible"
      :title="previewTitle"
      :width="isMobile ? '100%' : '800px'"
      :footer="null"
      @cancel="handlePreviewCancel"
      :style="isMobile ? { top: 0, margin: 0, maxWidth: '100%' } : { top: '8vh' }"
      :bodyStyle="isMobile ? { padding: '10px', height: 'calc(100vh - 55px)', overflow: 'hidden' } : {}"
    >
      <div v-if="previewType === 'pdf'" style="max-height: 80vh; overflow-y: scroll; display: flex; flex-direction: column; align-items: center;">
         <div style="margin-bottom: 10px; display: flex; gap: 10px; align-items: center;">
           <a-button :disabled="pdfPage <= 1" @click="changePage(-1)">上一页</a-button>
           <span>{{ pdfPage }} / {{ pdfPageCount }}</span>
           <a-button :disabled="pdfPage >= pdfPageCount" @click="changePage(1)">下一页</a-button>
         </div>
         <VuePdfEmbed
            :source="previewContent"
            :page="pdfPage"
            text-layer
            annotation-layer
            @loaded="handlePdfLoaded"
            style="width: 100%; border: 1px solid #eee;"
         />
      </div>
      <div v-else-if="previewType === 'markdown'" class="markdown-body" style="max-height: 70vh; overflow-y: auto;" v-html="md.render(previewContent)"></div>
      <div v-else-if="previewType === 'image'" style="text-align: center;">
          <img :src="previewContent" style="max-width: 100%; max-height: 70vh;" />
      </div>
      <pre v-else style="white-space: pre-wrap; word-wrap: break-word; max-height: 70vh; overflow-y: auto;">{{ previewContent }}</pre>
    </a-modal>

    <a-drawer
        v-model:visible="chunksDrawerVisible"
        title="切片预览"
        :width="isMobile ? '100%' : 600"
        @close="closeChunksDrawer">
      <a-list
          :loading="chunksLoading"
          item-layout="vertical"
          :data-source="chunksList"
      >
        <template #renderItem="{ item }">
          <a-list-item>
            <a-list-item-meta :title="`Chunk #${item.chunkIndex}`" />
            <div style="white-space: pre-wrap; background: #f5f5f5; padding: 10px; border-radius: 4px;">{{ item.text }}</div>
            <div style="margin-top: 8px; color: #999; font-size: 12px;">Token Length: {{ item.tokenLength }}</div>
          </a-list-item>
        </template>
        <template #loadMore>
          <div
              v-if="!chunksLoading && hasMoreChunks"
              :style="{ textAlign: 'center', marginTop: '12px', height: '32px', lineHeight: '32px' }"
          >
            <a-button @click="loadMoreChunks">加载更多</a-button>
          </div>
        </template>
      </a-list>
    </a-drawer>

    <!-- 邀请用户对话框 -->
    <a-modal
        v-model:visible="inviteModalVisible"
        title="邀请用户访问知识库"
        :confirm-loading="inviteSubmitting"
        @ok="handleInviteSubmit"
    >
      <a-form :model="inviteFormData" :label-col="{ span: 6 }" :wrapper-col="{ span: 18 }">
        <a-form-item label="用户名或邮箱" required>
          <a-input v-model:value="inviteFormData.userIdentifier" placeholder="请输入用户名或邮箱"/>
        </a-form-item>
        <a-alert 
          message="只有私有知识库可以邀请用户。被邀请的用户将获得查看和使用该知识库的权限，但无法上传或修改文档" 
          type="info" 
          show-icon 
          style="margin-top: 12px;"
        />
      </a-form>
    </a-modal>

    <!-- 被邀请用户列表对话框 -->
    <a-modal
        v-model:visible="invitedUsersModalVisible"
        title="被邀请用户列表"
        :footer="null"
        width="800px"
    >
      <a-table
          :columns="invitedUsersColumns"
          :data-source="invitedUsers"
          :loading="loadingInvitedUsers"
          :pagination="false"
          row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'grantedAt'">
            {{ new Date(record.grantedAt).toLocaleString() }}
          </template>
          <template v-if="column.key === 'action'">
            <a-button
                type="link"
                danger
                @click="handleRemoveInvitedUser(record)">
              移除
            </a-button>
          </template>
        </template>
      </a-table>
    </a-modal>

    <!-- 上传进度对话框 -->
    <a-modal
        v-model:visible="uploadProgressModalVisible"
        title="上传进度"
        :footer="null"
        :maskClosable="false" 
        width="600px"
    >
      <div style="max-height: 400px; overflow-y: auto;">
        <a-list :data-source="uploadProgressList" item-layout="horizontal">
          <template #renderItem="{ item }">
            <a-list-item>
               <a-list-item-meta :title="item.name">
                  <template #description>
                     <a-progress :percent="item.percent" :status="item.status === 'error' ? 'exception' : (item.status === 'done' ? 'success' : 'active')" />
                     <div v-if="item.status === 'error'" style="color: red">{{ item.error }}</div>
                  </template>
               </a-list-item-meta>
            </a-list-item>
          </template>
        </a-list>
      </div>
      <div style="text-align: right; margin-top: 16px;">
        <a-button @click="uploadProgressModalVisible = false">关闭</a-button>
      </div>
    </a-modal>

    <!-- 下载/预览进度对话框 -->
    <a-modal
        v-model:visible="downloadProgress.visible"
        :title="downloadProgress.title"
        :footer="null"
        :closable="false"
        :maskClosable="false"
        width="400px"
        :centered="true"
    >
      <div style="padding: 24px 0; text-align: center;">
        <a-progress :percent="downloadProgress.percent" status="active" />
        <div style="margin-top: 16px; color: #666;">
          正在使用魔法为你生成数据中...
        </div>
      </div>
    </a-modal>
  </div>
</template>

<style scoped>
:deep(.markdown-body p) {
  margin-bottom: 0;
}
.markdown-body {
    line-height: 1.6;
}

.kb-header {
  margin-bottom: 16px; 
  display: flex; 
  justify-content: space-between; 
  align-items: center;
}

.kb-title-container {
  display: flex; 
  align-items: center; 
  gap: 16px;
}

.kb-title {
  margin: 0;
}

.kb-actions {
  display: flex; 
  gap: 8px;
}

@media (max-width: 768px) {
  .kb-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .kb-title-container {
    width: 100%;
  }
  
  .kb-title {
    font-size: 18px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  
  .kb-actions {
    width: 100%;
    justify-content: space-between;
    flex-wrap: wrap;
  }

  .kb-actions .ant-btn {
    flex: 1;
    min-width: 40px;
    padding: 4px 8px;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  
  .kb-actions .ant-upload-wrapper {
    flex: 1;
  }
  
  .kb-actions .ant-upload-wrapper .ant-btn {
    width: 100%;
  }
}
</style>