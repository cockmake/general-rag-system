<script setup>
import zhCN from 'ant-design-vue/es/locale/zh_CN';
import { useThemeStore } from './stores/theme';
import { storeToRefs } from 'pinia';

const themeStore = useThemeStore();
const { algorithm } = storeToRefs(themeStore); // Reactive algorithm requires special handling usually, but let's try direct access first or computed
</script>

<template>
  <a-config-provider :locale="zhCN" :theme="{ algorithm: themeStore.algorithm() }">
    <router-view />
  </a-config-provider>
</template>

<style scoped>

</style>
