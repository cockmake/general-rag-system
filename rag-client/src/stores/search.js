import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSearchStore = defineStore('search', () => {
  const keyword = ref('')
  const results = ref([])
  const offset = ref(0)
  const hasMore = ref(true)
  const scrollPosition = ref(0)

  // Actions
  const setKeyword = (val) => {
    keyword.value = val
  }

  const setResults = (val) => {
    results.value = val
  }
  
  const appendResults = (newResults) => {
    results.value.push(...newResults)
  }

  const setOffset = (val) => {
    offset.value = val
  }

  const setHasMore = (val) => {
    hasMore.value = val
  }
  
  const setScrollPosition = (val) => {
    scrollPosition.value = val
  }
  
  const clearState = () => {
    keyword.value = ''
    results.value = []
    offset.value = 0
    hasMore.value = true
    scrollPosition.value = 0
  }

  const removeItem = (sessionId) => {
    results.value = results.value.filter(item => item.sessionId !== sessionId)
  }

  return {
    keyword,
    results,
    offset,
    hasMore,
    scrollPosition,
    setKeyword,
    setResults,
    appendResults,
    setOffset,
    setHasMore,
    setScrollPosition,
    clearState,
    removeItem
  }
})
