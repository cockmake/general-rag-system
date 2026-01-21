import commonApi from './commonApi'

/**
 * Get the latest notification
 */
export function fetchLatestNotification() {
    return commonApi.get('/notifications/latest')
}
