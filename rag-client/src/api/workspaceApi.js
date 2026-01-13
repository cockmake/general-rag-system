// src/api/workspaceApi.js
import commonApi from './commonApi'

/**
 * 工作空间相关 API
 */
export const workspaceApi = {
    /**
     * 获取工作空间列表
     * @returns {Promise} 包含 owned、member、current 的工作空间列表
     */
    getWorkspaces() {
        return commonApi.get('/workspaces/list')
    },

    /**
     * 创建工作空间
     * @param {Object} data - 工作空间数据
     * @param {string} data.name - 工作空间名称
     * @param {string} data.description - 工作空间描述
     * @returns {Promise} 创建的工作空间
     */
    createWorkspace(data) {
        return commonApi.post('/workspaces', data)
    },

    /**
     * 更新工作空间信息
     * @param {number} workspaceId - 工作空间ID
     * @param {Object} data - 更新数据
     * @param {string} data.name - 工作空间名称
     * @param {string} data.description - 工作空间描述
     * @returns {Promise}
     */
    updateWorkspace(workspaceId, data) {
        return commonApi.put(`/workspaces/${workspaceId}`, data)
    },

    /**
     * 删除工作空间
     * @param {number} workspaceId - 工作空间ID
     * @returns {Promise}
     */
    deleteWorkspace(workspaceId) {
        return commonApi.delete(`/workspaces/${workspaceId}`)
    },

    /**
     * 切换当前工作空间
     * @param {number} workspaceId - 工作空间ID
     * @returns {Promise}
     */
    switchWorkspace(workspaceId) {
        return commonApi.post(`/workspaces/${workspaceId}/switch`)
    },

    /**
     * 邀请用户加入工作空间
     * @param {Object} data - 邀请数据
     * @param {number} data.workspaceId - 工作空间ID
     * @param {string} data.userIdentifier - 用户名或邮箱
     * @returns {Promise}
     */
    inviteUser(data) {
        return commonApi.post('/workspaces/invite', data)
    },

    /**
     * 获取工作空间成员列表
     * @param {number} workspaceId - 工作空间ID
     * @returns {Promise} 成员列表
     */
    getMembers(workspaceId) {
        return commonApi.get(`/workspaces/${workspaceId}/members`)
    },

    /**
     * 移除工作空间成员
     * @param {number} workspaceId - 工作空间ID
     * @param {number} userId - 用户ID
     * @returns {Promise}
     */
    removeMember(workspaceId, userId) {
        return commonApi.delete(`/workspaces/${workspaceId}/members/${userId}`)
    }
}

export default workspaceApi
