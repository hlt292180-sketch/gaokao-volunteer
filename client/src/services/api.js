// API 请求层 —— 封装所有后端接口调用
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',       // Vite proxy 转发到 Flask :3000
  timeout: 10000,
})

// 🔒 请求拦截器：自动带 JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 🔒 响应拦截器：统一错误处理
api.interceptors.response.use(
  (res) => res.data,      // 直接返回 res.data，不用每次 .data
  (err) => {
    const msg = err.response?.data?.message || '网络请求失败'
    if (err.response?.status === 401) {
      localStorage.removeItem('token'); localStorage.removeItem('user')
    }
    return Promise.reject(new Error(msg))
  }
)

// ===== 公开接口 =====
export const getProvinces = () => api.get('/provinces/')
export const convertScore = (params) => api.get('/score-segments/convert', { params })
export const getUniversities = (params) => api.get('/universities/', { params })
export const getUniversity = (id) => api.get(`/universities/${id}`)
export const getMajors = (params) => api.get('/majors/', { params })
export const getMajor = (id) => api.get(`/majors/${id}`)
export const getMajorTrend = (id) => api.get(`/majors/${id}/trend`)

// ===== 认证接口 =====
export const register = (data) => api.post('/auth/register', data)
export const login = (data) => api.post('/auth/login', data)
export const getMe = () => api.get('/auth/me')

// ===== 测评接口（需登录）=====
export const getQuestions = () => api.get('/assessments/questions')
export const submitAssessment = (data) => api.post('/assessments/submit', data)
export const getLatestResult = () => api.get('/assessments/latest')

// ===== 志愿接口（需登录）=====
export const checkVolunteer = (data) => api.post('/volunteer/check', data)
export const generatePlan = (data) => api.post('/volunteer/generate', data)
export const getPlans = (params) => api.get('/volunteer/plans', { params })
export const getPlan = (id) => api.get(`/volunteer/plans/${id}`)
export const deletePlan = (id) => api.delete(`/volunteer/plans/${id}`)
export const deletePlansBatch = (ids) => api.delete('/volunteer/plans/batch', { data: { ids } })

// ===== 支付接口（需登录）=====
export const createPayment = (data) => api.post('/payment/create', data)
export const getPendingPayments = () => api.get('/payment/pending')
export const approvePayment = (orderNo) => api.post(`/payment/approve/${orderNo}`)

// ===== 统计埋点（公开）=====
export const trackEvent = (data) => api.post('/analytics/track', data).catch(() => {})
export const getAnalyticsStats = (params) => api.get('/analytics/stats', { params })
export const getFunnel = (params) => api.get('/analytics/funnel', { params })

// ===== 收藏接口（需登录）=====
export const getFavUniversities = () => api.get('/favorites/universities')
export const favUniversity = (id) => api.post('/favorites/universities/' + id)
export const unfavUniversity = (id) => api.delete('/favorites/universities/' + id)
export const getFavMajors = () => api.get('/favorites/majors')
export const favMajor = (id) => api.post('/favorites/majors/' + id)
export const unfavMajor = (id) => api.delete('/favorites/majors/' + id)
export const checkFav = (type, ids) => api.get('/favorites/check?type=' + type + '&ids=' + ids.join(','))

export default api  // 用于需要直接调用 api.get/post 的场景
