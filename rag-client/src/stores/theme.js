import { defineStore } from 'pinia';
import { ref } from 'vue';
import { theme } from 'ant-design-vue';

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref(localStorage.getItem('theme') === 'dark');
  
  const toggleTheme = () => {
    isDark.value = !isDark.value;
    localStorage.setItem('theme', isDark.value ? 'dark' : 'light');
    applyTheme();
  };

  const applyTheme = () => {
    if (isDark.value) {
      document.body.setAttribute('data-theme', 'dark');
    } else {
      document.body.removeAttribute('data-theme');
    }
  };

  // Initial apply
  applyTheme();

  return {
    isDark,
    toggleTheme,
    algorithm: () => isDark.value ? theme.darkAlgorithm : theme.defaultAlgorithm,
  };
});
