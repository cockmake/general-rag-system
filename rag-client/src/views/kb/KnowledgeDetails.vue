<script setup>
import {onMounted, ref, computed, watch} from "vue";
import {onUnmounted} from "vue";
import VuePdfEmbed from 'vue-pdf-embed';
import 'vue-pdf-embed/dist/styles/annotationLayer.css';
import 'vue-pdf-embed/dist/styles/textLayer.css';
import md from "@/utils/markdown.js";
import {useRoute, useRouter} from "vue-router";
import {message} from "ant-design-vue";
import {
  LoadingOutlined,
  ArrowLeftOutlined,
  FolderOutlined,
  FileOutlined,
  HomeOutlined,
  MoreOutlined,
  DownOutlined
} from '@ant-design/icons-vue';
import {
  deleteDocument,
  previewDocument,
  listDocuments,
  uploadDocument,
  renameDocument,
  listChunks,
  inviteUserToKb,
  getInvitedUsers,
  removeInvitedUser,
  fetchAvailableKbs,
  updateKb
} from "@/api/kbApi.js";
import {useUserStore} from "@/stores/user";

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const kbId = route.params.kbId;
const fileList = ref([]);
const uploading = ref(false);
const currentKb = ref(null);
const currentPath = ref([]);

const currentPathString = computed(() => {
  return currentPath.value.join('/');
});

const getRelativePath = (fullPath) => {
  const prefix = currentPathString.value ? currentPathString.value + '/' : '';
  if (!fullPath.startsWith(prefix)) return null;
  return fullPath.substring(prefix.length);
};

const displayList = computed(() => {
  const list = [];
  const folders = new Set();

  if (!fileList.value) return [];

  // Sort files first to ensure consistent order
  const sortedFiles = [...fileList.value].sort((a, b) => (a.fileName || '').localeCompare(b.fileName || ''));

  sortedFiles.forEach(file => {
    // Normalize path separators just in case
    const fileName = (file.fileName || '').replace(/\\/g, '/');
    const rel = getRelativePath(fileName);
    if (rel === null) return; // Not in current folder

    // Ignore if it's exactly the folder itself (shouldn't happen with files but just in case)
    if (rel === '') return;

    const parts = rel.split('/');
    if (parts.length > 1) {
      // It's in a subfolder
      const folderName = parts[0];
      if (!folders.has(folderName)) {
        folders.add(folderName);

        // Calculate folder stats
        const prefix = (currentPathString.value ? currentPathString.value + '/' : '') + folderName + '/';
        const filesInFolder = fileList.value.filter(f => (f.fileName || '').replace(/\\/g, '/').startsWith(prefix));

        let totalSize = 0;
        let status = 'ready';
        let hasProcessing = false;
        let hasFailed = false;

        filesInFolder.forEach(f => {
          totalSize += (f.fileSize || 0);
          if (f.status === 'failed') hasFailed = true;
          if (f.status === 'processing') hasProcessing = true;
        });

        if (hasFailed) status = 'failed';
        else if (hasProcessing) status = 'processing';

        list.push({
          id: 'folder-' + folderName, // unique key for UI
          fileName: folderName,
          isFolder: true,
          fileSize: totalSize,
          status: status,
          createdAt: file.createdAt, // Just use one of the files' date
        });
      }
    } else {
      // It's a file in current folder
      list.push({
        ...file,
        isFolder: false
      });
    }
  });

  // Sort folders first, then files
  return list.sort((a, b) => {
    if (a.isFolder && !b.isFolder) return -1;
    if (!a.isFolder && b.isFolder) return 1;
    return a.fileName.localeCompare(b.fileName);
  });
});

const enterFolder = (folderName) => {
  currentPath.value.push(folderName);
};

const navToLevel = (index) => {
  if (index === -1) {
    currentPath.value = [];
  } else {
    currentPath.value = currentPath.value.slice(0, index + 1);
  }
};

const handleDeleteFolder = async (folderName) => {
  const prefix = (currentPathString.value ? currentPathString.value + '/' : '') + folderName + '/';
  // Find all files that start with this prefix
  const filesToDelete = fileList.value.filter(f => {
    const fn = (f.fileName || '').replace(/\\/g, '/');
    return fn.startsWith(prefix);
  });

  if (filesToDelete.length === 0) {
    message.warning('空文件夹或无法找到文件');
    return;
  }

  const hide = message.loading(`正在删除 ${filesToDelete.length} 个文件...`, 0);
  try {
    // Execute sequentially to avoid overwhelming server or hitting rate limits
    // Or parallel with limit. 
    // Since we don't have a batch delete API, we loop.
    for (const file of filesToDelete) {
      await deleteDocument(kbId, file.id);
    }
    message.success('文件夹删除成功');
    fetchDocuments();
  } catch (e) {
    console.error(e);
    message.error('部分文件删除失败，请重试');
    fetchDocuments(); // Refresh to see what's left
  } finally {
    hide();
  }
};

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
1. 文档中的信息仅供参考
2. 如果文档不足以完整回答，结合对话历史进行推理或明确说明
3. 文档中的信息为切片信息，可能语义并不连贯或存在错误，你需要抽取或推理相关信息`;

const acceptExtensions = ".md,.txt,.pdf,.json,.py,.java,.js,.ts,.vue,.html,.xml,.yml,.sh,.rb,.css,.scss,.jpg,.jpeg,.png,.gif,.bmp,.webp";

const invitedUsersColumns = [
  {title: '用户名', dataIndex: 'username', key: 'username'},
  {title: '邮箱', dataIndex: 'email', key: 'email'},
  {title: '邀请人', dataIndex: 'grantedByUsername', key: 'grantedByUsername'},
  {title: '邀请时间', dataIndex: 'grantedAt', key: 'grantedAt'},
  {title: '操作', key: 'action', width: 100}
];

const columns = [
  {title: '', key: 'icon', width: 50, align: 'center'},
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
// 用于追踪文件夹上传的文件数量
const folderUploadFileSet = ref(new Set());
const folderUploadChecked = ref(false);
const folderUploadBlocked = ref(false); // 标记本次文件夹上传是否已被阻止
const MAX_FOLDER_FILES = 300;

// 自动排除的文件夹列表
const EXCLUDED_FOLDERS = [
  'node_modules',
  '.git',
  '.venv',
  'venv',
  'dist',
  'build',
  '.idea',
  '.vscode',
  '__pycache__',
  '.pytest_cache',
  '.mypy_cache',
  'target',
  'vendor',
  '.gradle',
  '.next',
  '.nuxt'
];

// 检查文件路径是否在排除列表中
const isFileExcluded = (filePath) => {
  const pathParts = filePath.split('/');
  return EXCLUDED_FOLDERS.some(excluded => pathParts.includes(excluded));
};

const beforeUpload = (file, fileList) => {
  const extension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
  const allowed = acceptExtensions.split(',');
  if (!allowed.includes(extension)) {
    message.error(`不支持的文件类型: ${file.name}`);
    return false; // 阻止上传
  }

  // 检测是否是文件夹上传（通过 webkitRelativePath 判断）
  if (file.webkitRelativePath) {
    // 检查文件是否在排除列表中
    if (isFileExcluded(file.webkitRelativePath)) {
      console.log(`文件已自动排除: ${file.webkitRelativePath}`);
      return false; // 自动排除，不上传
    }

    // 如果本次文件夹上传已被阻止，直接返回 false，不再弹窗
    if (folderUploadBlocked.value) {
      return false;
    }

    // 首次检测到文件夹上传时，统计递归扫描的所有文件数量
    if (!folderUploadChecked.value) {
      folderUploadFileSet.value.clear();

      // fileList 包含本次上传的所有文件（递归扫描文件夹及所有子文件夹）
      if (fileList && fileList.length > 0) {
        // 统计所有有效文件（排除自动排除列表中的文件夹）
        let totalFiles = 0;
        let excludedFiles = 0;

        fileList.forEach(f => {
          if (f.webkitRelativePath) {
            if (isFileExcluded(f.webkitRelativePath)) {
              excludedFiles++;
            } else {
              folderUploadFileSet.value.add(f.uid);
              totalFiles++;
            }
          }
        });

        console.log(`文件夹递归扫描完成，有效文件数: ${totalFiles}，已排除文件数: ${excludedFiles}`);

        // 如果排除了文件，提示用户
        if (excludedFiles > 0) {
          message.info(`已自动排除 ${excludedFiles} 个开发环境文件（如 node_modules、.git 等）`, 3);
        }

        // 检查文件总数是否超过限制
        if (totalFiles > MAX_FOLDER_FILES) {
          // 只弹出一次警告
          message.warning(`检测到有效文件数量为 ${totalFiles}，超过最大限制 ${MAX_FOLDER_FILES}。请检查是否包含不必要的大文件或文件夹，最大文件数量为 ${MAX_FOLDER_FILES}。`, 5);
          folderUploadChecked.value = false;
          folderUploadBlocked.value = true; // 标记为已阻止
          folderUploadFileSet.value.clear();

          // 延迟重置阻止状态，为下次上传做准备
          setTimeout(() => {
            folderUploadBlocked.value = false;
          }, 1000);

          return false;
        }
      }

      folderUploadChecked.value = true;
    }

    // 所有文件检查通过后，在最后一个文件处理完后重置状态
    if (folderUploadFileSet.value.size > 0) {
      folderUploadFileSet.value.delete(file.uid);
      if (folderUploadFileSet.value.size === 0) {
        folderUploadChecked.value = false;
      }
    }
  } else {
    // 单文件上传，重置文件夹上传状态
    folderUploadChecked.value = false;
    folderUploadFileSet.value.clear();
    folderUploadBlocked.value = false;
  }

  return true;
};

const MAX_CONCURRENT_UPLOADS = 5;
const concurrentUploads = ref(0);
const uploadQueue = [];

const processQueue = async () => {
  if (uploadQueue.length === 0 || concurrentUploads.value >= MAX_CONCURRENT_UPLOADS) {
    return;
  }

  while (uploadQueue.length > 0 && concurrentUploads.value < MAX_CONCURRENT_UPLOADS) {
    const task = uploadQueue.shift();
    concurrentUploads.value++;

    const {formData, file, onSuccess, onError} = task;

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
      concurrentUploads.value--;
      activeUploadsCount.value--;
      if (activeUploadsCount.value === 0) {
        uploading.value = false;
      }
      processQueue();
    }
  }
};

const customRequest = async (options) => {
  const {file, onSuccess, onError} = options;

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
  // Use webkitRelativePath if available (folder upload), otherwise fallback to name.
  // We explicitly set the filename in formData to include the path.
  const prefix = currentPathString.value ? currentPathString.value + '/' : '';
  const relativePath = file.webkitRelativePath || file.name;
  const fullPath = prefix + relativePath;
  formData.append('files', file, fullPath);

  // Add to queue and process
  uploadQueue.push({formData, file, onSuccess, onError});
  processQueue();
};

// 2. 预览逻辑
const handlePreview = async (record) => {
  downloadProgress.value = {visible: true, percent: 0, title: '正在加载预览...'};
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
  downloadProgress.value = {visible: true, percent: 0, title: '正在准备下载...'};
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
  <div style="padding: 24px; height: 100vh; display: flex; flex-direction: column;">
    <div class="kb-header" style="flex-shrink: 0;">
      <div class="kb-title-container">
        <a-button @click="goBack" type="text" shape="circle">
          <template #icon>
            <arrow-left-outlined/>
          </template>
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
            directory
            multiple>
          <a-button>
            <span v-if="!isMobile">📂 上传文件夹</span>
            <span v-else>📂</span>
          </a-button>
        </a-upload>
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

    <!-- Breadcrumb -->
    <div style="margin-bottom: 16px; flex-shrink: 0;">
      <a-breadcrumb>
        <a-breadcrumb-item>
          <a @click="navToLevel(-1)">
            <home-outlined/>
            根目录</a>
        </a-breadcrumb-item>
        <a-breadcrumb-item v-for="(folder, index) in currentPath" :key="index">
          <a @click="navToLevel(index)">{{ folder }}</a>
        </a-breadcrumb-item>
      </a-breadcrumb>
    </div>

    <a-table :columns="columns" :data-source="displayList" row-key="id" :pagination="false"
             :scroll="{ x: 800, y: 'calc(100vh - 250px)' }">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'icon'">
          <folder-outlined v-if="record.isFolder" style="color: #1890ff; font-size: 18px;"/>
          <file-outlined v-else style="color: #666; font-size: 18px;"/>
        </template>
        <template v-if="column.key === 'fileName'">
          <a v-if="record.isFolder" @click="enterFolder(record.fileName)" style="font-weight: bold;">
            {{ record.fileName }}
          </a>
          <span v-else>{{ record.fileName.split('/').pop() }}</span>
        </template>
        <template v-if="column.key === 'fileSize'">
          <span>{{ (record.fileSize / (1024 * 1024)).toFixed(2) }} MB</span>
        </template>
        <template v-if="column.key === 'status'">
          <template v-if="record.isFolder">
            <a-tag v-if="record.status === 'processing'" color="blue">
              <loading-outlined/>
              向量化中
            </a-tag>
            <a-tag v-else-if="record.status === 'ready'" color="green">完成</a-tag>
            <a-tag v-else-if="record.status === 'failed'" color="red">失败</a-tag>
          </template>
          <template v-else>
            <a-tag v-if="record.status === 'processing'" color="blue">
              <loading-outlined/>
              向量化中
            </a-tag>
            <a-tag v-else-if="record.status === 'ready'" color="green">完成</a-tag>
            <a-tag v-else-if="record.status === 'failed'" color="red">失败</a-tag>
            <a-tag v-else color="default">{{ record.status }}</a-tag>
          </template>
        </template>
        <template v-if="column.key === 'action'">
          <template v-if="record.isFolder">
            <a-popconfirm
                title="确定要删除这个文件夹及其所有内容吗？"
                ok-text="确定"
                cancel-text="取消"
                @confirm="handleDeleteFolder(record.fileName)"
            >
              <a-button type="link" danger size="small">删除</a-button>
            </a-popconfirm>
          </template>
          <template v-else>
            <!-- Mobile View: Dropdown -->
            <a-dropdown v-if="isMobile" :trigger="['click']">
              <a-button type="text" size="small">
                <more-outlined/>
              </a-button>
              <template #overlay>
                <a-menu>
                  <a-menu-item @click="handlePreview(record)">预览</a-menu-item>
                  <a-menu-item @click="handleDownload(record)">下载</a-menu-item>
                  <a-menu-item @click="handlePreviewChunks(record)">预览切片</a-menu-item>
                  <a-menu-item @click="openRenameModal(record)">重命名</a-menu-item>
                  <a-menu-item danger>
                    <a-popconfirm
                        title="确定要删除这个文件吗？"
                        ok-text="确定"
                        cancel-text="取消"
                        @confirm="handleDelete(record)"
                    >
                      <span>删除</span>
                    </a-popconfirm>
                  </a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>

            <!-- Desktop View: Buttons -->
            <span v-else>
                  <a-button type="link" size="small" @click="handlePreview(record)">预览</a-button>
                  <a-divider type="vertical"/>
                  <a-button type="link" size="small" @click="handlePreviewChunks(record)">切片</a-button>
                  <a-divider type="vertical"/>
                  
                  <a-dropdown>
                    <a class="ant-dropdown-link" @click.prevent style="font-size: 12px">
                      更多 <down-outlined/>
                    </a>
                    <template #overlay>
                      <a-menu>
                        <a-menu-item @click="handleDownload(record)">
                            下载文件
                        </a-menu-item>
                        <a-menu-item @click="openRenameModal(record)">
                            重命名
                        </a-menu-item>
                        <a-menu-item danger>
                            <a-popconfirm
                                title="确定要删除这个文件吗？"
                                ok-text="确定"
                                cancel-text="取消"
                                @confirm="handleDelete(record)"
                            >
                                <div style="width: 100%">删除文件</div>
                            </a-popconfirm>
                        </a-menu-item>
                      </a-menu>
                    </template>
                  </a-dropdown>
              </span>
          </template>
        </template>
      </template>
    </a-table>

    <a-modal
        v-model:visible="renameModalVisible"
        title="重命名文件"
        @ok="handleRename"
    >
      <a-input v-model:value="newFileName" placeholder="请输入新文件名"/>
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
      <div v-if="previewType === 'pdf'"
           style="max-height: 80vh; overflow-y: scroll; display: flex; flex-direction: column; align-items: center;">
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
      <div v-else-if="previewType === 'markdown'" class="markdown-body" style="max-height: 70vh; overflow-y: auto;"
           v-html="md.render(previewContent)"></div>
      <div v-else-if="previewType === 'image'" style="text-align: center;">
        <img :src="previewContent" style="max-width: 100%; max-height: 70vh;"/>
      </div>
      <pre v-else style="white-space: pre-wrap; word-wrap: break-word; max-height: 70vh; overflow-y: auto;">{{
          previewContent
        }}</pre>
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
            <a-list-item-meta :title="`Chunk #${item.chunkIndex}`"/>
            <div style="white-space: pre-wrap; background: #f5f5f5; padding: 10px; border-radius: 4px;">{{
                item.text
              }}
            </div>
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
      <!-- 整体进度统计 -->
      <div style="padding: 12px; background: #f5f5f5; border-radius: 4px; margin-bottom: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <span style="font-weight: 500;">整体进度</span>
          <span style="font-size: 16px; font-weight: 600; color: #1890ff;">
            {{ uploadProgressList.filter(item => item.status === 'done').length }} / {{ uploadProgressList.length }}
          </span>
        </div>
        <a-progress
            :percent="Math.round((uploadProgressList.filter(item => item.status === 'done').length / uploadProgressList.length) * 100)"
            :status="uploadProgressList.some(item => item.status === 'error') ? 'exception' : (uploadProgressList.filter(item => item.status === 'done').length === uploadProgressList.length ? 'success' : 'active')"
            :show-info="false"
        />
        <div style="display: flex; gap: 16px; margin-top: 8px; font-size: 12px; color: #666;">
          <span>✅ 成功: {{ uploadProgressList.filter(item => item.status === 'done').length }}</span>
          <span>⏳ 进行中: {{ uploadProgressList.filter(item => item.status === 'uploading').length }}</span>
          <span v-if="uploadProgressList.filter(item => item.status === 'error').length > 0" style="color: #ff4d4f;">
            ❌ 失败: {{ uploadProgressList.filter(item => item.status === 'error').length }}
          </span>
        </div>
      </div>

      <div style="max-height: 400px; overflow-y: auto;">
        <a-list :data-source="uploadProgressList" item-layout="horizontal">
          <template #renderItem="{ item }">
            <a-list-item>
              <a-list-item-meta :title="item.name">
                <template #description>
                  <a-progress :percent="item.percent"
                              :status="item.status === 'error' ? 'exception' : (item.status === 'done' ? 'success' : 'active')"/>
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
        <a-progress :percent="downloadProgress.percent" status="active"/>
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