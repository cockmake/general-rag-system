import commonApi from './commonApi'

/**
 * 获取最近活动日志
 * @param {number} limit 限制条数
 */
export function fetchRecentActivities(limit = 10) {
    return commonApi.get('/audit-logs/recent', { limit })
}
