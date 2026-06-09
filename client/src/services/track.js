// 埋点工具 —— 记录用户行为事件，发送到后端 /api/analytics/track
import { trackEvent } from './api'

/**
 * 检测设备类型
 */
function getDeviceType() {
  const ua = navigator.userAgent || ''
  if (/Mobi|Android|iPhone|iPad/i.test(ua)) return 'mobile'
  return 'desktop'
}

/**
 * 发送埋点事件（fire-and-forget，不阻塞页面）
 * @param {string} eventType - 事件类型
 * @param {object} extra - 额外字段 { score, rank }
 */
export function track(eventType, extra = {}) {
  const payload = {
    event_type: eventType,
    device_type: getDeviceType(),
    ...extra,
  }
  // 用 navigator.sendBeacon 或直接发请求，失败不影响页面
  trackEvent(payload)
}
