import {ref, nextTick} from 'vue'

export function useScroll() {
  const messagesContainer = ref(null)
  const userScrolledUp = ref(false)
  const isAutoScrolling = ref(false)

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

  return {
    messagesContainer,
    userScrolledUp,
    isAutoScrolling,
    scrollToBottom,
    handleScroll
  }
}
