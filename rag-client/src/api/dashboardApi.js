import commonApi from './commonApi'

/**
 * Get dashboard summary statistics
 */
export function fetchDashboardSummary() {
    return commonApi.get('/dashboard/summary')
}
