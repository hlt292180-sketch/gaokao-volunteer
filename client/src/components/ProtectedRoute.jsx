// 登录保护路由 —— 未登录自动跳转登录页
import { Navigate } from 'react-router-dom'
import useAuthStore from '../store/authStore'

export default function ProtectedRoute({ children }) {
  // 双重检查：Zustand 内存 + localStorage，防止渲染时序导致误判
  const token = useAuthStore((s) => s.token) || localStorage.getItem('token')
  if (!token) return <Navigate to="/login" replace />
  return children
}
