import { create } from 'zustand'

// 用户信息
interface User {
  id: number
  username: string
  role: 'admin' | 'owner' | 'editor' | 'viewer' | 'guest'
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (token: string, user: User) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  login: (token, user) => {
    localStorage.setItem('auth_token', token)
    localStorage.setItem('auth_user', JSON.stringify(user))
    set({ token, user, isAuthenticated: true })
  },
  logout: () => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_user')
    set({ token: null, user: null, isAuthenticated: false })
  },
}))

// 应用状态
interface AppState {
  sidebarOpen: boolean
  currentPage: string
  loading: boolean
  error: string | null
  toggleSidebar: () => void
  setCurrentPage: (page: string) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
}

export const useAppStore = create<AppState>((set) => ({
  sidebarOpen: true,
  currentPage: 'dashboard',
  loading: false,
  error: null,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setCurrentPage: (page) => set({ currentPage: page }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}))

// 内容管理状态
interface ContentState {
  contents: any[]
  loading: boolean
  error: string | null
  refreshContents: () => void
  setContents: (contents: any[]) => void
}

export const useContentStore = create<ContentState>((set) => ({
  contents: [],
  loading: false,
  error: null,
  refreshContents: () => {
    // 触发内容刷新
    set({ contents: [] })
  },
  setContents: (contents) => set({ contents }),
}))

// 通知状态
interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  message: string
  duration?: number
}

interface NotificationState {
  notifications: Notification[]
  addNotification: (notification: Omit<Notification, 'id'>) => void
  removeNotification: (id: string) => void
  clearNotifications: () => void
}

export const useNotificationStore = create<NotificationState>((set) => ({
  notifications: [],
  addNotification: (notification) => {
    const id = Date.now().toString()
    set((state) => ({
      notifications: [...state.notifications, { ...notification, id }],
    }))
    // 自动移除
    if (notification.duration !== 0) {
      setTimeout(() => {
        set((state) => ({
          notifications: state.notifications.filter((n) => n.id !== id),
        }))
      }, notification.duration || 3000)
    }
  },
  removeNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    })),
  clearNotifications: () => set({ notifications: [] }),
}))