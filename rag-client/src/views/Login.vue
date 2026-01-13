<script setup>
import {reactive, ref} from 'vue'
import {useRouter} from 'vue-router'
import {message} from 'ant-design-vue'

import {useUserStore} from '@/stores/user'
import md5 from 'crypto-js/md5';

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
  <div class="login-page">
    <div class="login-card">
      <h2 class="title">RAG 系统登录</h2>

      <a-form
          :model="formState"
          :rules="rules"
          layout="vertical"
          @finish="onLogin"
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
        <a @click="router.push('/register')">没有账号？去注册</a>
      </div>
    </div>
  </div>
</template>

<style scoped>
.footer-actions {
  text-align: center;
  margin-top: 16px;
}

.login-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}

.login-card {
  width: 360px;
  padding: 32px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.06);
}

.title {
  text-align: center;
  margin-bottom: 24px;
}

.hint {
  margin-top: 12px;
  text-align: center;
  color: #999;
  font-size: 12px;
}
</style>
