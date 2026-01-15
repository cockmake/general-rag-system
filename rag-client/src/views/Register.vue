<script setup>
import { reactive, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import md5 from 'crypto-js/md5'
import commonApi from '@/api/commonApi'
import AuthLayout from '@/layouts/AuthLayout.vue';

const router = useRouter()
const loading = ref(false)
const sendCodeLoading = ref(false)
const countdown = ref(0)
let timer = null

const formState = reactive({
  username: '',
  password: '',
  email: '',
  code: ''
})

const rules = {
  username: [{ required: true, message: '请输入账号' }],
  password: [{ required: true, message: '请输入密码' }],
  email: [
    { required: true, message: '请输入邮箱' },
    { type: 'email', message: '请输入正确的邮箱格式' }
  ],
  code: [{ required: true, message: '请输入验证码' }]
}

const sendCode = async () => {
  if (!formState.email) {
    message.warning('请先输入邮箱')
    return
  }
  
  sendCodeLoading.value = true
  try {
    await commonApi.post('/users/send-code', { email: formState.email })
    message.success('验证码已发送')
    countdown.value = 60
    timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
      }
    }, 1000)
  } catch (e) {
    // Error is handled by interceptor usually, or display e.message
    console.error(e)
  } finally {
    sendCodeLoading.value = false
  }
}

const onRegister = async () => {
  loading.value = true
  try {
    await commonApi.post('/users/register', {
      username: formState.username,
      password: md5(formState.password).toString(),
      email: formState.email,
      code: formState.code
    })
    message.success('注册成功，请登录')
    router.push('/login')
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<template>
  <AuthLayout>
    <div class="register-wrapper">
      <div class="auth-header">
        <h2 class="title">创建账号</h2>
        <p class="subtitle">注册 RAG 系统，开启智能知识库之旅</p>
      </div>

      <a-form
        :model="formState"
        :rules="rules"
        layout="vertical"
        @finish="onRegister"
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

        <a-form-item label="邮箱" name="email">
          <a-input
            v-model:value="formState.email"
            placeholder="请输入邮箱"
            size="large"
          />
        </a-form-item>

        <a-form-item label="验证码" name="code">
          <div class="code-container">
            <a-input
              v-model:value="formState.code"
              placeholder="请输入验证码"
              size="large"
            />
            <a-button
              class="code-btn"
              size="large"
              :loading="sendCodeLoading"
              :disabled="countdown > 0"
              @click="sendCode"
            >
              {{ countdown > 0 ? `${countdown}s 后重试` : '获取验证码' }}
            </a-button>
          </div>
        </a-form-item>

        <a-form-item>
          <a-button
            type="primary"
            html-type="submit"
            size="large"
            block
            :loading="loading"
          >
            注册
          </a-button>
        </a-form-item>
        
        <div class="footer-actions">
          <span class="text-gray">已有账号？</span>
          <a @click="goToLogin">立即登录</a>
        </div>
      </a-form>
    </div>
  </AuthLayout>
</template>

<style scoped>
.register-wrapper {
  width: 100%;
  max-width: 400px;
  padding: 0 24px;
}

.auth-header {
  margin-bottom: 24px;
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

.code-container {
  display: flex;
  gap: 8px;
}

.code-btn {
  width: 120px;
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
</style>
