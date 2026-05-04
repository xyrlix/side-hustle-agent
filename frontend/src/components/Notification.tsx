import { useEffect } from 'react'
import { message } from 'antd'
import { useNotificationStore } from '../store'

// 全局通知显示组件
export function NotificationDisplay() {
  const { notifications } = useNotificationStore()

  useEffect(() => {
    notifications.forEach((n) => {
      switch (n.type) {
        case 'success':
          message.success(n.message)
          break
        case 'error':
          message.error(n.message)
          break
        case 'warning':
          message.warning(n.message)
          break
        case 'info':
          message.info(n.message)
          break
      }
    })
  }, [notifications])

  return null
}

// 通知 API
export const notify = {
  success: (msg: string, duration = 3000) =>
    useNotificationStore.getState().addNotification({ type: 'success', message: msg, duration }),
  error: (msg: string, duration = 4000) =>
    useNotificationStore.getState().addNotification({ type: 'error', message: msg, duration }),
  warning: (msg: string, duration = 3000) =>
    useNotificationStore.getState().addNotification({ type: 'warning', message: msg, duration }),
  info: (msg: string, duration = 3000) =>
    useNotificationStore.getState().addNotification({ type: 'info', message: msg, duration }),
}