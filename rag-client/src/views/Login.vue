<script setup>
import {reactive, ref} from 'vue'
import {useRouter} from 'vue-router'
import {message} from 'ant-design-vue'

import {useUserStore} from '@/stores/user'
import md5 from 'crypto-js/md5';
import AuthLayout from '@/layouts/AuthLayout.vue';
import { GithubOutlined } from '@ant-design/icons-vue';

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)


/**
 * 登录表单
 */
const formState = reactive({
  username: '',
  password: ''
})

/**
 * 表单校验规则
 */
const rules = {
  username: [{required: true, message: '请输入账号'}],
  password: [{required: true, message: '请输入密码'}]
}

/**
 * Mock 登录（开发期）
 * 输入任意账号密码即可
 */
const onLogin = async () => {
  loading.value = true
  try {
    /**
     * 模拟后端返回的数据结构
     * 与 userStore.login 保持一致
     */
    await userStore.login({
      username: formState.username,
      password: md5(formState.password).toString(),
      rememberMe: true
    })

    message.success('登录成功')

    router.push('/dashboard')
  } catch (e) {
    message.error('登录失败')
  } finally {

    loading.value = false
  }
}
</script>

<template>
  <AuthLayout>
    <div class="login-wrapper">
      <div class="auth-header">
        <h2 class="title">欢迎回来</h2>
        <p class="subtitle">登录您的账号以继续</p>
      </div>

      <a-form
          :model="formState"
          :rules="rules"
          layout="vertical"
          @finish="onLogin"
          class="auth-form"
      >
        <a-form-item label="账号" name="username">
          <a-input
              v-model:value="formState.username"
              placeholder="请输入账号"
              size="large"
          />
        </a-form-item>

        <a-form-item label="密码" name="password">
          <a-input-password
              v-model:value="formState.password"
              placeholder="请输入密码"
              size="large"
          />
        </a-form-item>

        <a-form-item>
          <a-button
              type="primary"
              html-type="submit"
              size="large"
              block
              :loading="loading"
          >
            登录
          </a-button>
        </a-form-item>
      </a-form>

      <div class="footer-actions">
        <span class="text-gray">还没有账号？</span>
        <a style="cursor: pointer" @click="router.push('/register')">立即注册</a>
      </div>
      
      <div class="github-link">
        <a href="https://github.com/cockmake/general-rag-system" target="_blank">
          <github-outlined /> GitHub 开源地址
        </a>
      </div>
    </div>
  </AuthLayout>
</template>

<style scoped>
.login-wrapper {
  width: 100%;
  max-width: 360px;
  padding: 0 24px;
}

.auth-header {
  margin-bottom: 32px;
  text-align: center;
}

.title {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 8px;
  color: #333;
}

.subtitle {
  color: #666;
  font-size: 14px;
}

.auth-form {
  margin-bottom: 24px;
}

.footer-actions {
  text-align: center;
  margin-top: 16px;
  font-size: 14px;
}

.text-gray {
  color: #999;
  margin-right: 8px;
}

.github-link {
  text-align: center;
  margin-top: 24px;
}

.github-link a {
  color: #666;
  font-size: 14px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  transition: color 0.3s;
}

.github-link a:hover {
  color: #1677ff;
}
</style>
