// 认证状态管理（Zustand）
import { create } from 'zustand'
import { login as loginApi, register as registerApi, getMe } from '../services/api'

const useAuthStore = create((set, get) => ({
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  token: localStorage.getItem('token') || null,
  loading: false,

  loginAction: async (phone, password) => {
    set({ loading: true })
    try {
      const res = await loginApi({ phone, password })
      const { token, user } = res.data
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(user))
      set({ token, user, loading: false })
      return { success: true }
    } catch (err) {
      set({ loading: false })
      return { success: false, message: err.message }
    }
  },

  registerAction: async (phone, password, nickname) => {
    set({ loading: true })
    try {
      await registerApi({ phone, password, nickname })
      set({ loading: false })
      return get().loginAction(phone, password)
    } catch (err) {
      set({ loading: false })
      return { success: false, message: err.message }
    }
  },

  refreshUser: async () => {
    if (!get().token) return null
    try {
      const res = await getMe()
      localStorage.setItem('user', JSON.stringify(res.data))
      set({ user: res.data })
      return res.data
    } catch { get().logout(); return null }
  },

  logout: () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    set({ user: null, token: null })
  },
}))

export default useAuthStore
