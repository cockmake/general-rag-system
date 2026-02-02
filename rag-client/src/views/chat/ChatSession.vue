<script setup>
import {h, onMounted, onUnmounted, ref, watch, nextTick, computed, reactive} from 'vue'
import {
  UserOutlined,
  CopyOutlined,
  EditOutlined,
  ReloadOutlined,
  CheckOutlined,
  CloseOutlined,
  GlobalOutlined,
  FileSearchOutlined,
  CodeOutlined,
  AppstoreOutlined,
  BulbOutlined,
  CaretRightOutlined,
} from '@ant-design/icons-vue';
import {Bubble, Sender, ThoughtChain} from 'ant-design-x-vue';
import {useRoute} from 'vue-router'
import {
  fetchAvailableModels,
  fetchSessionMessages,
  startChatStream,
  editMessageStream,
  retryMessageStream
} from '@/api/chatApi'
import {
  Typography, Button, Space, message as antMessage,
  theme, Input, Spin, Tooltip, Collapse,
  CollapsePanel
} from "ant-design-vue";
import {findKbById, groupedModels, loadKbs, models, selectedKb, selectedModel} from "@/vars.js";
import KbSelector from "@/components/KbSelector.vue";
import {useThemeStore} from '@/stores/theme';

// --- Markdown 相关引入 ---
import markdownit from 'markdown-it';
import taskLists from 'markdown-it-task-lists';
import mj from 'markdown-it-mathjax3';
import hljs from "highlight.js";
import 'highlight.js/styles/atom-one-light.css';
import Paragraph from "ant-design-vue/es/typography/Paragraph.js";

const question = ref('')
const route = useRoute()
const sessionId = ref(route.params.sessionId)
const messages = ref([])
const loading = ref(false)
const isGenerating = ref(false)
const {token} = theme.useToken()
const themeStore = useThemeStore();

// 自动滚动相关
const messagesContainer = ref(null)
const userScrolledUp = ref(false)
const isAutoScrolling = ref(false)

// 选中的工具
const selectedTools = ref([])
const thinkingEnabled = ref(false)
const isRestoring = ref(false) // 标记是否正在恢复会话状态
const isUserUncheckedWebSearch = ref(false) // 标记用户是否手动取消了webSearch
const allKnownTools = ['webSearch']
const toolConfigs = {
  'webSearch': {icon: GlobalOutlined, label: '联网', desc: '开启联网搜索'},
  'web_extractor': {icon: FileSearchOutlined, label: '网页', desc: '网页提取'},
  'code_interpreter': {icon: CodeOutlined, label: '代码', desc: '代码解释器'},
}

const currentModel = computed(() => {
  if (!selectedModel.value) return null
  return models.value.find(m => m.modelId === selectedModel.value) || null
})

const availableTools = computed(() => {
  if (!currentModel.value || !currentModel.value.metadata) return []
  // 后端已统一返回对象，直接读取 tools
  return currentModel.value.metadata.tools || []
})

const toggleTool = (toolKey) => {
  if (!availableTools.value.includes(toolKey)) return
  const index = selectedTools.value.indexOf(toolKey)
  if (index === -1) {
    selectedTools.value.push(toolKey)
    if (toolKey === 'webSearch') isUserUncheckedWebSearch.value = false
  } else {
    selectedTools.value.splice(index, 1)
    if (toolKey === 'webSearch') isUserUncheckedWebSearch.value = true
  }
}

const toggleThinking = () => {
  if (currentModel.value?.metadata?.thinking?.editable === false) return
  thinkingEnabled.value = !thinkingEnabled.value
}

const handleThinkingCollapseChange = (index, keys) => {
  if (!Array.isArray(messages.value) || index < 0 || index >= messages.value.length) return
  const msg = messages.value[index]
  if (!msg) return
  const normalized = Array.isArray(keys) ? keys : (keys ? [keys] : [])
  msg.thinkingCollapseKeys = normalized
}

watch(selectedModel, () => {
  // 模型切换时，校验并重置工具
  const newSupported = availableTools.value
  selectedTools.value = selectedTools.value.filter(t => newSupported.includes(t))

  // 如果支持 webSearch，且用户没有手动取消（isUserUncheckedWebSearch 为 false），则默认勾选
  // 注意：在恢复模式下 (isRestoring=true) 不要自动勾选，完全信任 loadSession 的恢复逻辑
  if (!isRestoring.value && newSupported.includes('webSearch')) {
     if (!isUserUncheckedWebSearch.value && !selectedTools.value.includes('webSearch')) {
       selectedTools.value.push('webSearch')
     }
  }

  // 仅在非恢复状态下重置思考模型配置
  if (!isRestoring.value) {
    if (currentModel.value?.metadata?.thinking) {
      const {default: isDefault, editable} = currentModel.value.metadata.thinking
      // 如果不可编辑，必须强制设为默认值；如果可编辑，也重置为默认值（因为切换模型了）
      // 所以这里逻辑一样，但为了代码清晰和未来维护，保持 isDefault 赋值
      thinkingEnabled.value = isDefault
    } else {
      thinkingEnabled.value = false
    }
  }
})

// 编辑相关
const editingIndex = ref(-1)
const editingContent = ref('')

const langAliases = {
  'js': 'javascript',
  'ts': 'typescript',
  'py': 'python',
  'h5': 'html',
  'rb': 'ruby',
  'sh': 'bash',
  'c++': 'cpp',
}
const md = markdownit({
  html: true,
  linkify: true,
  typographer: true,
  highlight: function (str, lang) {
    lang = langAliases[lang] || lang;
    if (lang && hljs.getLanguage(lang)) {
      try {
        return '<pre class="hljs"><code>'
            + hljs.highlight(str, {language: lang, ignoreIllegals: true}).value +
            '</code></pre>';
      } catch (__) {
      }
    }
    const result = hljs.highlightAuto(str)
    return '<pre class="hljs"><code>' + result.value + '</code></pre>';
  }
}).use(mj, {
  tex: {
    inlineMath: [['$', '$'], ['\\(', '\\)']],
    displayMath: [['$$', '$$'], ['\\[', '\\]']],
    processEscapes: true
  },
  options: {
    skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code'],
    ignoreHtmlClass: 'tex2jax_ignore'
  }
}).use(taskLists);

const assistantAvatar = {
  color: '#f56a00',
  backgroundColor: '#fde3cf',
};

const userAvatar = {
  color: '#fff',
  backgroundColor: '#87d068',
};

// 滚动到底部
const scrollToBottom = (behavior = 'smooth') => {
  if (!messagesContainer.value || userScrolledUp.value) return

  isAutoScrolling.value = true
  nextTick(() => {
    const container = messagesContainer.value
    if (container) {
      container.scrollTo({
        top: container.scrollHeight,
        behavior: behavior
      })
    }
    // 等待滚动完成后重置标志
    setTimeout(() => {
      isAutoScrolling.value = false
    }, behavior === 'smooth' ? 300 : 0)
  })
}

// 监听用户滚动
const handleScroll = () => {
  if (isAutoScrolling.value || !messagesContainer.value) return

  const container = messagesContainer.value
  const threshold = 50 // 距离底部的阈值
  const distanceToBottom = container.scrollHeight - container.scrollTop - container.clientHeight

  // 如果用户滚动到接近底部，认为用户想要自动滚动
  if (distanceToBottom < threshold) {
    userScrolledUp.value = false
  } else {
    // 用户向上滚动了
    userScrolledUp.value = true
  }
}

// 监听消息变化，自动滚动
// 移除 messages.value.length 的监听，合并到 deep watcher 中处理，或者使用 ant-design-x-vue 内置的 auto-scroll
// 移除自动滚动逻辑，由用户控制
/*
let scrollTimeout = null
watch(
    messages,
    () => {
      if (!userScrolledUp.value) {
        if (scrollTimeout) return
        scrollTimeout = setTimeout(() => {
          scrollToBottom()
          scrollTimeout = null
        }, 100) // 100ms 节流
      }
    },
    {deep: true}
)
*/

const handleStreamCallbacks = (assistantMsg, userMsg = null) => {
  // 流开始时设置用户消息状态为generating
  if (userMsg) {
    userMsg.status = 'generating'
  }
  return {
    onOpen: () => {
    },
    onMessage: (data) => {
      if (data.type === 'content') {
        if (assistantMsg.loading) assistantMsg.loading = false
        assistantMsg.content += data.content
      } else if (data.type === 'thinking') {
        if (assistantMsg.loading) assistantMsg.loading = false
        // 收到思考内容时，自动展开
        if (!assistantMsg.thinkingCollapseKeys || assistantMsg.thinkingCollapseKeys.length === 0) {
             assistantMsg.thinkingCollapseKeys = ['thinking-panel']
        }
        if (typeof assistantMsg.thinking === "string") {
          assistantMsg.thinking += data.content
        } else {
          assistantMsg.thinking = data.content
        }
      } else if (data.type === 'process') {
        // 第一次收到 process 消息时就取消 loading 状态
        if (assistantMsg.loading) assistantMsg.loading = false

        // 处理检索过程信息
        if (!assistantMsg.ragProcess) {
          assistantMsg.ragProcess = []
        }
        const processInfo = data.payload

        // 查找是否已存在相同 step 和 status 的步骤
        const existingIndex = assistantMsg.ragProcess.findIndex(
            p => p.step === processInfo.step && p.status === processInfo.status
        )

        if (existingIndex !== -1) {
          // 如果是相同的 step 和 status，更新该步骤
          assistantMsg.ragProcess[existingIndex] = processInfo
        } else {
          // 否则添加为新步骤（running 和 completed 会作为不同的项）
          assistantMsg.ragProcess.push(processInfo)
        }
      } else if (data.type === 'done') {
        // 流完成，更新消息ID和状态
        if (userMsg) {
          if (data.userMessageId) {
            userMsg.id = data.userMessageId
          }
          userMsg.status = 'completed'
        }
        if (data.assistantMessageId) {
          assistantMsg.id = data.assistantMessageId
        }
        assistantMsg.status = 'completed'
        assistantMsg.loading = false
        // 思考结束，收起面板
        if (assistantMsg.thinking) {
          assistantMsg.thinkingCollapseKeys = []
        }
      } else if (data.type === 'usage') {
        // 处理 usage 信息
        if (data.payload) {
          if (data.payload.latency_ms) {
            assistantMsg.latencyMs = data.payload.latency_ms
          }
          if (data.payload.completion_tokens) {
            assistantMsg.completionTokens = data.payload.completion_tokens
          }
        }
      }
    },
    onError: (err) => {
      assistantMsg.content += `\n[Error: 请求发起失败！]`
      assistantMsg.loading = false
      isGenerating.value = false
      // 错误时设置用户消息状态为pending，允许重试
      if (userMsg) {
        userMsg.status = 'pending'
      }
    },
    onClose: () => {
      // 流完成时更新状态为completed
      assistantMsg.loading = false
      assistantMsg.status = 'completed'
      isGenerating.value = false
      if (userMsg) {
        userMsg.status = 'completed'
      }
    }
  }
}

const loadSession = async (newSessionId) => {
  loading.value = true
  isRestoring.value = true
  messages.value = []
  models.value = await fetchAvailableModels().then()
  await loadKbs()
  let data = await fetchSessionMessages(newSessionId)
  if (data.length > 0) {
    const lastMsg = data[data.length - 1]
    // 恢复模型选择
    if (lastMsg.modelId && models.value.find(m => m.modelId === lastMsg.modelId)) {
      selectedModel.value = lastMsg.modelId
    } else {
      selectedModel.value = selectedModel.value || null
    }
    // 恢复知识库选择
    if (isKbSupported.value && lastMsg.kbId && findKbById(lastMsg.kbId)) {
      selectedKb.value = lastMsg.kbId
    } else {
      selectedKb.value = null
    }
  } else {
    selectedModel.value = selectedModel.value || null
    selectedKb.value = null
  }

  messages.value = data.map(msg => {
    let ragProcess = null
    if (msg.ragContext && msg.role === 'assistant') {
      try {
        ragProcess = typeof msg.ragContext === 'string' ? JSON.parse(msg.ragContext) : msg.ragContext
      } catch (e) {
        console.error('Failed to parse ragContext:', e)
      }
    }

    // Parse options if present
    let options = null
    if (msg.options) {
      try {
        options = typeof msg.options === 'string' ? JSON.parse(msg.options) : msg.options
      } catch (e) {
        console.error('Failed to parse options:', e)
      }
    }
    return reactive({
      id: msg.id,
      role: msg.role,
      content: msg.content,
      status: msg.status,
      loading: msg.role === 'assistant' && msg.status === 'generating',
      ragProcess: ragProcess,
      latencyMs: msg.latencyMs,
      completionTokens: msg.completionTokens,
      options: options,
      thinking: msg.thinking,
      thinkingCollapseKeys: [] // 默认折叠
    })
  })

  // 初始化时，根据最后一条用户消息的 options 同步工具选择状态
  const lastUserMsg = messages.value.filter(m => m.role === 'user').pop()
  if (lastUserMsg && lastUserMsg.options) {
    const opts = lastUserMsg.options
    // 重置 selectedTools
    selectedTools.value = []
    if (opts.webSearch) {
      selectedTools.value.push('webSearch')
      isUserUncheckedWebSearch.value = false
    } else {
      // 存在 options 但 webSearch 为 false/undefined，说明之前可能用户取消了
      // 如果支持webSearch但opts里没有，视为用户取消
      if (currentModel.value?.metadata?.tools?.includes('webSearch')) {
         isUserUncheckedWebSearch.value = true
      }
    }

    // 恢复思考状态
    if (opts.thinking) {
      thinkingEnabled.value = true
    } else {
      thinkingEnabled.value = false
    }

    // 如果模型配置了 thinking 且 editable 为 false，强制使用 default 值
    if (currentModel.value?.metadata?.thinking?.editable === false) {
      thinkingEnabled.value = currentModel.value.metadata.thinking.default
    }

    // 后续如果有其他 tool，也在这里添加逻辑
  } else {
    // 如果没有历史 options，默认清空 (或者保留默认值? 根据需求，这里先清空以保持一致性)
    // 修改策略：如果是新会话（无options），且支持webSearch，则默认选中
    selectedTools.value = []
    if (availableTools.value.includes('webSearch')) {
       selectedTools.value.push('webSearch')
       isUserUncheckedWebSearch.value = false
    } else {
       isUserUncheckedWebSearch.value = false
    }

    // 默认初始化思考状态
    if (currentModel.value?.metadata?.thinking) {
      thinkingEnabled.value = currentModel.value.metadata.thinking.default
    } else {
      thinkingEnabled.value = false
    }

    // 如果存在历史消息但没有options (旧数据)，尝试推断
    if (lastUserMsg) {
      thinkingEnabled.value = false
    }
  }

  if (data.length > 0) {
    const lastMsg = data[data.length - 1]
    if (lastMsg.role === 'user' && lastMsg.status === 'pending') {
      // 找到最后一条用户消息的引用
      const userMsg = messages.value[messages.value.length - 1]
      messages.value.push(reactive({
        role: 'assistant',
        content: '',
        loading: true,
        ragProcess: [],
        latencyMs: 0,
        completionTokens: 0,
        thinkingCollapseKeys: [] // 默认折叠
      }))
      const assistant = messages.value[messages.value.length - 1]
      const {onOpen, onMessage, onError, onClose} = handleStreamCallbacks(assistant, userMsg)
      isGenerating.value = true

      let options = null
      if (lastMsg.options) {
        try {
          options = typeof lastMsg.options === 'string' ? JSON.parse(lastMsg.options) : lastMsg.options
        } catch (e) {
          console.error("Parse options failed", e)
        }
      }

      startChatStream(newSessionId, selectedModel.value, null, selectedKb.value || undefined, options, onOpen, onMessage, onError, onClose)
    }
  }
  loading.value = false
  // 加载完成后重置滚动状态并滚动到底部
  userScrolledUp.value = false
  nextTick(() => {
    scrollToBottom('auto') // 使用 auto 立即跳转到底部
    // 延迟重置恢复标记，确保 watcher 执行完毕
    setTimeout(() => {
      isRestoring.value = false
    }, 0)
  })
}

const isMobile = ref(false)

const checkIsMobile = () => {
  isMobile.value = window.innerWidth <= 768
}

onMounted(() => {
  checkIsMobile()
  window.addEventListener('resize', checkIsMobile)
  loadSession(sessionId.value)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkIsMobile)
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

watch(
    () => route.params.sessionId,
    (newId, oldId) => {
      if (newId && newId !== oldId) {
        // 切换会话时重置滚动状态
        userScrolledUp.value = false
        loadSession(newId)
        sessionId.value = newId
      }
    }
)

const onSend = (text) => {
  if (loading.value || isGenerating.value || isLastUserMsgGenerating.value) return
  question.value = ''
  // 发送新消息时重置滚动状态
  userScrolledUp.value = false
  const userMsg = reactive({role: 'user', content: text, status: 'pending'})
  messages.value.push(userMsg)
  messages.value.push(reactive({
    role: 'assistant',
    content: '',
    loading: true,
    ragProcess: [],
    latencyMs: 0,
    completionTokens: 0,
    thinkingCollapseKeys: [] // 默认折叠
  }))
  scrollToBottom()
  const assistant = messages.value[messages.value.length - 1]
  const {onOpen, onMessage, onError, onClose} = handleStreamCallbacks(assistant, userMsg)
  isGenerating.value = true

  const options = {}
  if (selectedTools.value.includes('webSearch')) {
    options.webSearch = true
  }

  // 思考模型参数
  if (currentModel.value?.metadata?.thinking && thinkingEnabled.value) {
    options.thinking = true
  }

  startChatStream(sessionId.value, selectedModel.value, text, isKbSupported.value ? (selectedKb.value || undefined) : undefined, options, onOpen, onMessage, onError, onClose)
}

const onCopy = (textToCopy) => {
  if (!textToCopy) {
    antMessage.warning('消息内容为空')
    return
  }
  navigator.clipboard.writeText(textToCopy).then(() => {
    antMessage.success('复制成功')
  }).catch(() => {
    antMessage.error('复制失败')
  })
}

// 获取最后一条用户消息
const lastUserMessage = computed(() => {
  const msgs = messages.value
  for (let i = msgs.length - 1; i >= 0; i--) {
    if (msgs[i].role === 'user') {
      return msgs[i]
    }
  }
  return null
})

// 最后一条用户消息是否正在生成
const isLastUserMsgGenerating = computed(() => {
  return lastUserMessage.value?.status === 'generating'
})

// 获取最后一条助手消息
const lastAssistantMessage = computed(() => {
  const msgs = messages.value
  for (let i = msgs.length - 1; i >= 0; i--) {
    if (msgs[i].role === 'assistant') {
      return msgs[i]
    }
  }
  return null
})

// 判断是否可以编辑/重试：只有最后一轮用户消息且非generating状态
const canEditOrRetry = computed(() => {
  const msg = lastUserMessage.value
  if (!msg) return false
  // 只有在完成或出错时才允许编辑/重试，generating和pending时不显示
  return ['completed', 'error'].includes(msg.status) || !msg.status
})

// 判断是否是最后一条用户消息
const isLastUserMessage = (item) => {
  const last = lastUserMessage.value
  if (!last) return false
  return item === last || (item.id && last.id && item.id === last.id)
}

// 判断是否是最后一条助手消息
const isLastAssistantMessage = (item) => {
  const last = lastAssistantMessage.value
  if (!last) return false
  return item === last || (item.id && last.id && item.id === last.id)
}

// 开始编辑（通过item）
const startEditByItem = (item) => {
  let index = messages.value.indexOf(item)

  // 如果通过引用找不到（可能是Proxy对象），尝试通过ID查找
  if (index === -1 && item.id) {
    index = messages.value.findIndex(m => m.id === item.id)
  }

  // 如果还是找不到，尝试查找最后一个用户消息（因为只有最后一个允许编辑）
  if (index === -1) {
    for (let i = messages.value.length - 1; i >= 0; i--) {
      if (messages.value[i].role === 'user') {
        // 简单的内容校验防止找错
        if (messages.value[i].content === item.content) {
          index = i
        }
        break
      }
    }
  }

  if (index === -1) {
    console.error('Cannot find message index for edit', item)
    return
  }

  editingIndex.value = index
  editingContent.value = item.content
}

// 取消编辑
const cancelEdit = () => {
  editingIndex.value = -1
  editingContent.value = ''
}

// 确认编辑并重新生成
const confirmEdit = () => {
  if (!editingContent.value.trim()) {
    antMessage.warning('问题内容不能为空')
    return
  }

  const index = editingIndex.value
  const userMsg = messages.value[index]

  // 更新本地消息内容
  userMsg.content = editingContent.value
  userMsg.status = 'pending'

  // 如果后面有助手消息，移除它
  if (index < messages.value.length - 1 && messages.value[index + 1].role === 'assistant') {
    messages.value.splice(index + 1, 1)
  }

  // 添加新的助手消息占位
  messages.value.push(reactive({
    role: 'assistant',
    content: '',
    loading: true,
    ragProcess: [],
    latencyMs: 0,
    completionTokens: 0,
    thinkingCollapseKeys: [] // 默认折叠
  }))
  const assistant = messages.value[messages.value.length - 1]
  const {onOpen, onMessage, onError, onClose} = handleStreamCallbacks(assistant, userMsg)

  isGenerating.value = true
  const options = {}
  if (selectedTools.value.includes('webSearch')) {
    options.webSearch = true
  }

  // 思考模型参数
  if (currentModel.value?.metadata?.thinking && thinkingEnabled.value) {
    options.thinking = true
  }

  // 调用编辑接口
  editMessageStream(
      userMsg.id,
      sessionId.value,
      selectedModel.value,
      isKbSupported.value ? (selectedKb.value || undefined) : undefined,
      editingContent.value,
      options,
      onOpen,
      onMessage,
      onError,
      onClose
  )

  // 重置编辑状态
  editingIndex.value = -1
  editingContent.value = ''
  userScrolledUp.value = false
}

// 重试AI回复
const onRetry = (userMsgIndex) => {
  const userMsg = messages.value[userMsgIndex]
  userMsg.status = 'pending'

  // 如果后面有助手消息，移除它
  if (userMsgIndex < messages.value.length - 1 && messages.value[userMsgIndex + 1].role === 'assistant') {
    messages.value.splice(userMsgIndex + 1, 1)
  }

  // 添加新的助手消息占位
  messages.value.push(reactive({
    role: 'assistant',
    content: '',
    loading: true,
    ragProcess: [],
    latencyMs: 0,
    completionTokens: 0,
    thinkingCollapseKeys: [] // 默认折叠
  }))
  const assistant = messages.value[messages.value.length - 1]
  const {onOpen, onMessage, onError, onClose} = handleStreamCallbacks(assistant, userMsg)

  isGenerating.value = true
  const options = {}
  if (selectedTools.value.includes('webSearch')) {
    options.webSearch = true
  }

  // 思考模型参数
  if (currentModel.value?.metadata?.thinking && thinkingEnabled.value) {
    options.thinking = true
  }

  // 调用重试接口
  retryMessageStream(
      userMsg.id,
      sessionId.value,
      selectedModel.value,
      isKbSupported.value ? (selectedKb.value || undefined) : undefined,
      options,
      onOpen,
      onMessage,
      onError,
      onClose
  )

  userScrolledUp.value = false
}

// 从助手消息触发重试（找到最后一个用户消息的索引）
const onRetryFromAssistant = () => {
  for (let i = messages.value.length - 1; i >= 0; i--) {
    if (messages.value[i].role === 'user') {
      onRetry(i)
      return
    }
  }
  antMessage.warning('没有找到可重试的用户消息')
}

const roles = computed(() => ({
  user: {
    placement: 'end',
    avatar: isMobile.value ? undefined : {icon: h(UserOutlined), style: userAvatar},
  },
  assistant: {
    placement: 'start',
    avatar: isMobile.value ? undefined : {icon: h(UserOutlined), style: assistantAvatar},
  },
}));
</script>

<template>
  <div class="chat-session-container" :class="{ 'is-dark': themeStore.isDark }">
    <!-- 顶部配置栏 removed -->
    <!-- <div class="chat-header">...</div> -->

    <!-- 消息列表区域 -->
    <div class="messages-container">
      <div
          ref="messagesContainer"
          class="messages-wrapper"
          @scroll="handleScroll">
        <Spin :spinning="loading">
          <Bubble.List
              auto-scroll
              :roles="roles"
              :items="messages"
              class="bubble-list">
            <template #header="{item: msg}">
              <!-- 显示 usage header -->
              <div v-if="msg.latencyMs || msg.completionTokens"
                   style="font-size: 12px; color: #999; margin-bottom: 8px;">
                <span v-if="msg.completionTokens">Tokens: {{ msg.completionTokens }}</span>
                <a-divider type="vertical" v-if="msg.completionTokens && msg.latencyMs"/>
                <span v-if="msg.latencyMs">Latency: {{ msg.latencyMs / 1000 }}s</span>
              </div>
            </template>
            <template #message="{ item: msg, index }">
              <div v-if="msg.role === 'assistant'" class="assistant-message">
                <!-- 显示检索过程 -->
                <ThoughtChain
                    v-if="msg.ragProcess && msg.ragProcess.length > 0"
                    :items="msg.ragProcess.map((p, idx) => {
                      const item = {
                        key: `${p.step}-${p.status}-${idx}`,
                        title: p.title || '处理中',
                        description: p.description || '',
                        status: p.status || 'pending'
                      }
                      if (p.content) {
                        item.content = h(Typography, {
                          innerHTML: md.render(p.content),
                        })
                      }
                      return item
                    })"
                    collapsible
                    class="thought-chain"
                />
                <!-- 显示思考过程 -->
                <div v-if="msg.thinking" class="thinking-section">
                  <a-collapse
                      ghost
                      size="small"
                      :bordered="false"
                      :activeKey="messages[index]?.thinkingCollapseKeys || []"
                      @change="(keys) => handleThinkingCollapseChange(index, keys)"
                      expand-icon-position="start"
                  >
                    <template #expandIcon="{ isActive }">
                      <div class="expand-icon-wrapper" :class="{ 'is-active': isActive }">
                        <CaretRightOutlined/>
                      </div>
                    </template>

                    <a-collapse-panel key="thinking-panel">
                      <template #header>
                        <div class="thinking-header-content">
                          <div class="thinking-title">
                            <BulbOutlined class="thinking-icon"/>
                            <span>深度思考过程</span>
                            <span v-if="(!messages[index]?.thinkingCollapseKeys || messages[index].thinkingCollapseKeys.length === 0) && msg.thinking" class="thinking-preview">
                               - {{ msg.loading && !msg.content ? '思考中...' : '已折叠' }}
                            </span>
                          </div>

                          <div v-if="msg.loading && !msg.content" class="thinking-status">
                            <span class="thinking-dots">思考中...</span>
                          </div>

                        </div>
                      </template>

                      <div class="thinking-content-wrapper">
                        <Typography>
                          <div
                              class="markdown-body thinking-markdown" v-html="md.render(msg.thinking || '')">
                          </div>
                        </Typography>
                      </div>

                    </a-collapse-panel>
                  </a-collapse>
                </div>

                <!-- 显示回答内容 -->
                <Typography>
                  <div class="markdown-body message-content" v-html="md.render(msg.content || '')"/>
                </Typography>
              </div>

              <div v-else class="user-message">
                <!-- 编辑模式 -->
                <div v-if="isLastUserMessage(msg) && editingIndex !== -1" class="edit-mode">
                  <a-textarea
                      v-model:value="editingContent"
                      :auto-size="{ minRows: 2, maxRows: 6 }"
                      class="edit-textarea"
                  />
                  <div class="edit-actions">
                    <a-button type="primary" size="small" :icon="h(CheckOutlined)" @click="confirmEdit">确认</a-button>
                    <a-button size="small" :icon="h(CloseOutlined)" @click="cancelEdit">取消</a-button>
                  </div>
                </div>
                <!-- 正常显示模式 -->
                <Typography v-else>
                  <div class="user-message-content">{{ msg.content || '' }}</div>
                </Typography>
              </div>
            </template>
            <template #footer="{ item, index }">
              <a-space :size="token.paddingXXS">
                <a-button
                    type="text"
                    size="small"
                    :icon="h(CopyOutlined)"
                    title="复制内容"
                    @click="onCopy(item.content)"/>
                <!-- 用户消息：编辑按钮 -->
                <a-button
                    v-if="item.role === 'user' && isLastUserMessage(item) && canEditOrRetry && editingIndex === -1"
                    type="text"
                    size="small"
                    :icon="h(EditOutlined)"
                    @click="startEditByItem(item)"
                    title="编辑问题"/>
                <!-- 助手消息：重试按钮 -->
                <a-button
                    v-if="item.role === 'assistant' && isLastAssistantMessage(item) && canEditOrRetry"
                    type="text"
                    size="small"
                    :icon="h(ReloadOutlined)"
                    @click="onRetryFromAssistant()"
                    title="重试回答"/>
              </a-space>
            </template>
          </Bubble.List>
        </Spin>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-container">
      <div class="input-wrapper">
        <Sender
            v-model:value="question"
            :loading="loading || isGenerating || isLastUserMsgGenerating"
            :actions="false"
            :auto-size="{ minRows: 2, maxRows: 6 }"
            @submit="onSend"
            class="chat-sender"
            placeholder="输入消息，Shift + Enter 换行，Enter 发送"
        >
          <!-- 工具栏 (Header插槽) -->
          <template #header>
            <div class="sender-header-tools" v-if="allKnownTools.length > 0 || currentModel?.metadata?.thinking">
              <div class="header-tools-wrapper">
                <!-- 思考模型开关 -->
                <div 
                  v-if="currentModel?.metadata?.thinking" 
                  class="header-tool-item"
                  :class="{ 
                    active: thinkingEnabled,
                    disabled: currentModel.metadata.thinking.editable === false
                  }"
                  @click="toggleThinking"
                  :title="currentModel.metadata.thinking.editable === false ? '当前模型强制开启或关闭思考，不可修改' : '开启深度思考模式'"
                >
                  <BulbOutlined />
                  <span>深度思考</span>
                  <CheckOutlined v-if="thinkingEnabled" style="font-size: 10px; margin-left: 2px;"/>
                </div>

                <template v-for="toolKey in allKnownTools" :key="toolKey">
                  <div
                      v-if="availableTools.includes(toolKey)"
                      class="header-tool-item"
                      :class="{
                        active: selectedTools.includes(toolKey)
                      }"
                      @click="toggleTool(toolKey)"
                      :title="toolConfigs[toolKey]?.desc || toolKey"
                  >
                    <component :is="toolConfigs[toolKey]?.icon || AppstoreOutlined"/>
                    <span>{{ toolConfigs[toolKey]?.label || toolKey }}</span>
                    <CheckOutlined v-if="selectedTools.includes(toolKey)" style="font-size: 10px; margin-left: 2px;"/>
                  </div>
                </template>
              </div>
            </div>
          </template>

          <template #footer="{ info: { components: { SendButton, LoadingButton } } }">
            <div class="sender-footer">
              <div class="sender-config">
                <a-select
                    v-model:value="selectedModel"
                    class="model-select-footer"
                    placeholder="选择模型"
                    :bordered="false"
                    :dropdownMatchSelectWidth="false"
                >
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

                <a-divider type="vertical" style="height: 16px; margin: 0 4px; border-left-color: rgba(0,0,0,0.1)"/>

                <div class="kb-wrapper">
                  <Tooltip :title="!isKbSupported ? '当前模型不支持知识库功能' : '请在您需要检索知识库中信息时选用'"
                           placement="topLeft">
                    <div style="width: 100%">
                      <KbSelector class="kb-select-footer" :disabled="!isKbSupported" :bordered="false" size="small"
                                  width="180px"/>
                    </div>
                  </Tooltip>
                </div>

                <!-- 聊天界面中的工具选择 (紧凑模式) - 已移除，移至 Header -->


              </div>
              <div class="sender-actions">
                <component :is="(loading || isGenerating || isLastUserMsgGenerating) ? LoadingButton : SendButton"
                           type="primary" :disabled="loading || isGenerating || isLastUserMsgGenerating || !question"
                           @click="!loading && !isGenerating && !isLastUserMsgGenerating && onSend(question)"/>
              </div>
            </div>
          </template>
        </Sender>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ================= 布局与容器 ================= */
.chat-session-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(to bottom, #f5f7fa 0%, #e8ecf1 100%);
}

.chat-header {
  padding: 12px 24px;
  flex-shrink: 0;
}

.header-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.header-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.header-content {
  display: flex;
  align-items: center;
  width: 100%;
}

.config-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.config-label-text {
  font-size: 14px;
  font-weight: 500;
  color: #666;
  white-space: nowrap;
}

.model-select,
.kb-select {
  min-width: 200px;
}

/* ================= 消息区域 ================= */
.messages-container {
  flex: 1;
  overflow: hidden;
  padding: 12px 24px;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.messages-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.bubble-list {
  min-height: 100%;
}

.assistant-message,
.user-message {
  animation: messageSlideIn 0.3s ease-out;
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.thought-chain {
  margin-bottom: 16px;
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.message-content {
  background: transparent;
  line-height: 1.8;
  font-size: 15px;
}

.user-message-content {
  line-height: 1.6;
  font-size: 15px;
  white-space: pre-wrap;
}

/* 编辑模式样式 */
.edit-mode {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 300px;
}

.edit-textarea {
  border-radius: 8px;
}

.edit-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

/* ================= 输入区域 & Sender ================= */
.input-container {
  flex-shrink: 0;
  padding: 12px 24px 16px;
}

.input-wrapper {
  max-width: 1200px;
  margin: 0 auto;
}

.chat-sender {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.chat-sender:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
}

.chat-sender:focus-within {
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.25);
}

.sender-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px 8px 4px;
}

.sender-config {
  display: flex;
  align-items: center;
  flex: 1;
  overflow-x: auto;
  gap: 4px;
}

.sender-config::-webkit-scrollbar {
  display: none;
}

.sender-actions {
  display: flex;
  gap: 8px;
  margin-left: 8px;
}

.model-select-footer {
  min-width: 120px;
}

.kb-select-footer {
  min-width: 160px;
  width: 180px; /* Default desktop width */
}

.sender-header-tools {
  padding: 8px 12px 4px;
}

.header-tools-wrapper {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.header-tool-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  color: #666;
  background: #f5f5f5;
  border: 1px solid transparent;
  transition: all 0.2s;
}

.header-tool-item:hover:not(.disabled) {
  background: #e6f7ff;
  color: #1890ff;
}

.header-tool-item.active {
  background: #e6f7ff;
  color: #1890ff;
  border-color: #1890ff;
  font-weight: 500;
}

.header-tool-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #f9f9f9;
  color: #999;
}

/* ================= Markdown 内部样式优化 ================= */
:deep(.markdown-body) {
  color: #24292f;
}

:deep(.markdown-body p) {
  margin-bottom: 0.8em;
  margin-top: 0;
}

:deep(.markdown-body h1),
:deep(.markdown-body h2),
:deep(.markdown-body h3) {
  margin-top: 1.2em;
  margin-bottom: 0.6em;
  font-weight: 600;
}

:deep(.markdown-body code) {
  background: rgba(175, 184, 193, 0.2);
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-size: 0.9em;
}

:deep(.markdown-body pre) {
  background: #f6f8fa;
  border-radius: 8px;
  padding: 16px;
  overflow-x: auto;
  margin: 1em 0;
}

:deep(.markdown-body blockquote) {
  border-left: 4px solid #667eea;
  padding-left: 1em;
  margin: 1em 0;
  color: #666;
}

:deep(.markdown-body ul),
:deep(.markdown-body ol) {
  padding-left: 2em;
  margin: 0.8em 0;
}

:deep(.markdown-body li) {
  margin: 0.4em 0;
}

:deep(.markdown-body table) {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
}

:deep(.markdown-body th),
:deep(.markdown-body td) {
  border: 1px solid #ddd;
  padding: 8px 12px;
}

:deep(.markdown-body th) {
  background: #f6f8fa;
  font-weight: 600;
}

/* ================= 滚动条样式 ================= */
.messages-wrapper::-webkit-scrollbar {
  width: 6px;
}

.messages-wrapper::-webkit-scrollbar-track {
  background: transparent;
}

.messages-wrapper::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.messages-wrapper::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}

:deep(.ant-spin-nested-loading),
:deep(.ant-spin-container) {
  height: 100%;
}

/* ================= 暗色模式 (Scoped部分) ================= */
/* 工具项暗色适配 */
.chat-session-container.is-dark .header-tool-item {
  background: rgba(255, 255, 255, 0.05);
  color: #a6a6a6;
}

.chat-session-container.is-dark .header-tool-item:hover:not(.disabled) {
  background: rgba(255, 255, 255, 0.1);
  color: #177ddc;
}

.chat-session-container.is-dark .header-tool-item.active {
  background: rgba(23, 125, 220, 0.2);
  color: #177ddc;
  border-color: #177ddc;
}

.chat-session-container.is-dark .header-tool-item.disabled {
  background: rgba(255, 255, 255, 0.02);
  color: #434343;
}

/* Sender Footer 暗色适配 */
.chat-session-container.is-dark .sender-footer {
  border-top-color: rgba(255, 255, 255, 0.1);
}

/* ================= 响应式设计 (合并) ================= */
@media (max-width: 768px) {
  .chat-header,
  .messages-container {
    padding: 8px 16px;
  }

  .header-content {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .config-group {
    width: 100%;
  }

  .model-select,
  .kb-select {
    flex: 1;
    min-width: 0;
  }

  .messages-wrapper {
    padding: 16px;
  }

  .input-container {
    padding: 8px 16px 12px;
  }

  /* Sender配置移动端适配 */
  .model-select-footer {
    width: auto !important;
    flex: 1;
    min-width: 90px;
  }

  .kb-wrapper {
    flex: 1;
    min-width: 0;
  }

  .kb-select-footer {
    width: 100% !important;
    min-width: 100px;
  }

  .sender-config {
    flex-wrap: nowrap;
  }
}
</style>

<style>
/* ================= 全局暗色模式覆盖 ================= */
/* 非 scoped 以确保优先级和覆盖 deep 结构或第三方组件 */

.chat-session-container.is-dark {
  background: linear-gradient(to bottom, #141414 0%, #1a1a1a 100%);
  color: #e0e0e0;
}

.chat-session-container.is-dark .header-card,
.chat-session-container.is-dark .messages-wrapper,
.chat-session-container.is-dark .chat-sender {
  background: #1e1e1e;
}

.chat-session-container.is-dark .header-card {
  background: rgba(30, 30, 30, 0.9);
}

.chat-session-container.is-dark .config-label-text {
  color: #aaa;
}

.chat-session-container.is-dark .markdown-body {
  color: #e0e0e0;
}

.chat-session-container.is-dark .markdown-body code {
  background: rgba(110, 118, 129, 0.4);
}

.chat-session-container.is-dark .markdown-body pre {
  background: #161b22;
}

.chat-session-container.is-dark .markdown-body blockquote {
  border-left-color: #a0aeff;
  color: #aaa;
}

.chat-session-container.is-dark .markdown-body th,
.chat-session-container.is-dark .markdown-body td {
  border-color: #444;
}

.chat-session-container.is-dark .markdown-body th {
  background: #161b22;
}

.chat-session-container.is-dark .messages-wrapper::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
}

.chat-session-container.is-dark .messages-wrapper::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* ================= 思考过程 (Thinking Section) ================= */
.thinking-section {
  margin-bottom: 16px;
  background: #f9f9fb; /* 极淡的蓝灰色背景 */
  border: 1px solid #eef0f5; /* 柔和边框 */
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
}

/* 头部样式 */
.thinking-header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  user-select: none;
  padding: 2px 0;
}

.thinking-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 500;
  color: #606266;
}

.thinking-icon {
  color: #f59e0b; /* 琥珀色灯泡 */
  font-size: 14px;
}

/* 展开图标 */
.expand-icon-wrapper {
  color: #909399;
  font-size: 10px;
  transition: transform 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
}

.expand-icon-wrapper.is-active {
  transform: rotate(90deg);
}

/* 思考状态 */
.thinking-status {
  font-size: 12px;
  color: #909399;
  display: flex;
  align-items: center;
}

.thinking-dots {
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    opacity: 0.4;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0.4;
  }
}

/* 内容区域 */
.thinking-content-wrapper {
  padding: 8px 16px 16px 36px; /* 左侧留白对齐标题文字 */
  position: relative;
}

.thinking-content-wrapper::before {
  content: '';
  position: absolute;
  left: 23px; /* 根据图标位置调整 */
  top: 0;
  bottom: 12px;
  width: 1px;
  background-color: #e0e0e0;
}

/* Markdown 模拟 Log/Draft 风格 */
.thinking-markdown {
  font-size: 14px !important;
  color: #444 !important;
  border-radius: 5px;
  padding: 10px;
}

.thinking-markdown pre {
  background: rgba(0, 0, 0, 0.03) !important;
  border: none !important;
  margin: 8px 0 !important;
  padding: 8px 12px !important;
}

.thinking-markdown code {
  background: rgba(0, 0, 0, 0.03) !important;
  font-size: 12px !important;
  color: #d63384 !important;
}

/* 去除 Collapse 组件默认干扰 */
.thinking-section .ant-collapse-header {
  padding: 8px 12px !important;
  align-items: center !important;
}

.thinking-section .ant-collapse-content-box {
  padding: 0 !important;
}

/* 思考过程 - 暗色模式适配 */
.chat-session-container.is-dark .thinking-section {
  background: rgba(255, 255, 255, 0.03);
  border-color: #303030;
}

.chat-session-container.is-dark .thinking-title {
  color: #a6a6a6;
}

.chat-session-container.is-dark .thinking-content-wrapper::before {
  background-color: #444;
}

.chat-session-container.is-dark .thinking-markdown {
  color: #999 !important;
}

.chat-session-container.is-dark .thinking-markdown pre,
.chat-session-container.is-dark .thinking-markdown code {
  background: rgba(255, 255, 255, 0.05) !important;
  color: #ccc !important;
}
</style>
