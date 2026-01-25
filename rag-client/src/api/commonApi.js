// src/api/commonApi.js
import axios from 'axios'
import {message, Modal} from 'ant-design-vue'
import {useUserStore} from '@/stores/user'
import {API_BASE_URL} from "../consts.js";

/**
 * Axios 实例
 */
const http = axios.create({
    baseURL: API_BASE_URL,
    withCredentials: false
})

/**
 * Request Interceptor
 * - 注入 Token
 * - 注入 Workspace / Tenant 信息
 */
http.interceptors.request.use(
    (config) => {
        const userStore = useUserStore()

        if (userStore.token) {
            config.headers.Authorization = `Bearer ${userStore.token}`
        }
        // 弹出请求中
        // message.info('请求中...').then()
        return config
    },
    (error) => Promise.reject(error)
)

/**
 * Response Interceptor
 * - 统一错误处理
 */
http.interceptors.response.use(
    (response) => {
        // 如果是 Blob 类型（文件下载/预览），直接返回
        if (response.config.responseType === 'blob') {
            return response.data
        }

        /**
         * 约定后端返回结构：
         * {
         *   code: 200,
         *   message: 'ok',
         *   data: any
         * }
         */
        const res = response.data
        if (res?.code !== 200) {
            handleBusinessError(res)
            return Promise.reject(res)
        }
        // message.success('操作成功').then()
        return res.data
    },
    (error) => {
        handleHttpError(error)
        return Promise.reject(error)
    }
)

/**
 * 业务错误（code != 0）
 */
function handleBusinessError(res) {
    switch (res.code) {
        case 401:
            Modal.warning({
                title: '登录已失效',
                content: res.message || '请重新登录',
                onOk: () => {
                    window.location.href = '/login'
                }
            })
            break
        case 403:
            message.error(res.message || '权限不足，无法执行该操作').then()
            break
        default:
            message.error(res.message || '操作失败').then()
    }
}

/**
 * HTTP 错误（网络 / 5xx）
 */
function handleHttpError(error) {
    if (!error.response) {
        message.error('网络异常，请检查连接').then()
        return
    }
    const {status} = error.response
    if (error.response.data.message) {
        message.error(error.response.data.message).then()
    } else if (status >= 500) {
        message.error('服务器异常，请稍后重试').then()
    } else {
        message.error(`错误代码：${status}`).then()
    }
}

/**
 * 通用方法封装
 */
export const commonApi = {
    get(url, params = null, config = {}) {
        return http.get(url, {params, ...config})
    },
    post(url, data = null, config = {}) {
        return http.post(url, data, config)
    },
    put(url, data = null, config = {}) {
        return http.put(url, data, config)
    },
    delete(url, params = null, config = {}) {
        return http.delete(url, {params, ...config})
    },

    /**
     * 文件上传（用于 documents）
     */
    upload(url, formData, config = {}) {
        return http.post(url, formData, {
            headers: {'Content-Type': 'multipart/form-data'},
            ...config
        })
    }
}

export default commonApi
