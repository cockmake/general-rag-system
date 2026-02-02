import {ref, computed, watch} from 'vue'
import {models, selectedModel} from '@/vars.js'

export function useTools() {
  const selectedTools = ref([])
  const thinkingEnabled = ref(false)
  const isRestoring = ref(false)
  const isUserUncheckedWebSearch = ref(false)

  const currentModel = computed(() => {
    if (!selectedModel.value) return null
    return models.value.find(m => m.modelId === selectedModel.value) || null
  })

  const availableTools = computed(() => {
    if (!currentModel.value || !currentModel.value.metadata) return []
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

  watch(selectedModel, () => {
    // 模型切换时，校验并重置工具
    const newSupported = availableTools.value
    selectedTools.value = selectedTools.value.filter(t => newSupported.includes(t))

    // 如果支持 webSearch，且用户没有手动取消，则默认勾选
    if (!isRestoring.value && newSupported.includes('webSearch')) {
      if (!isUserUncheckedWebSearch.value && !selectedTools.value.includes('webSearch')) {
        selectedTools.value.push('webSearch')
      }
    }

    // 仅在非恢复状态下重置思考模型配置
    if (!isRestoring.value) {
      if (currentModel.value?.metadata?.thinking) {
        const {default: isDefault} = currentModel.value.metadata.thinking
        thinkingEnabled.value = isDefault
      } else {
        thinkingEnabled.value = false
      }
    }
  })

  return {
    selectedTools,
    thinkingEnabled,
    isRestoring,
    isUserUncheckedWebSearch,
    currentModel,
    availableTools,
    toggleTool,
    toggleThinking
  }
}
