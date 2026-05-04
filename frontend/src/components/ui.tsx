import { Spin, Result, Button } from 'antd'
import { LoadingOutlined } from '@ant-design/icons'

// 加载状态组件
interface LoadingProps {
  tip?: string
  fullscreen?: boolean
}

export function Loading({ tip = '加载中...', fullscreen = false }: LoadingProps) {
  if (fullscreen) {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm z-50">
        <Spin indicator={<LoadingOutlined style={{ fontSize: 48, color: '#8b5cf6' }} spin />} />
        <span className="ml-4 text-white text-lg">{tip}</span>
      </div>
    )
  }
  return (
    <div className="flex flex-col items-center justify-center py-20">
      <Spin indicator={<LoadingOutlined style={{ fontSize: 48, color: '#8b5cf6' }} spin />} />
      <span className="mt-4 text-white/60 text-lg">{tip}</span>
    </div>
  )
}

// 空状态组件
interface EmptyStateProps {
  icon?: string
  title: string
  description?: string
  action?: {
    label: string
    onClick: () => void
  }
}

export function EmptyState({ icon = '📋', title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20">
      <div className="text-6xl mb-4 opacity-40">{icon}</div>
      <h3 className="text-xl font-bold text-white/80 mb-2">{title}</h3>
      {description && <p className="text-white/40 text-base mb-6">{description}</p>}
      {action && (
        <Button type="primary" onClick={action.onClick}>
          {action.label}
        </Button>
      )}
    </div>
  )
}

// 错误状态组件
interface ErrorStateProps {
  title?: string
  message: string
  onRetry?: () => void
}

export function ErrorState({ title = '出错了', message, onRetry }: ErrorStateProps) {
  return (
    <Result
      status="error"
      title={title}
      subTitle={message}
      extra={
        onRetry ? (
          <Button type="primary" onClick={onRetry}>
            重试
          </Button>
        ) : undefined
      }
    />
  )
}

// 确认对话框
interface ConfirmDialogProps {
  open: boolean
  title: string
  message: string
  onConfirm: () => void
  onCancel: () => void
  confirmText?: string
  cancelText?: string
  danger?: boolean
}

export function ConfirmDialog({
  open,
  title,
  message,
  onConfirm,
  onCancel,
  confirmText = '确认',
  cancelText = '取消',
  danger = false,
}: ConfirmDialogProps) {
  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black/80 backdrop-blur-sm" onClick={onCancel} />
      <div className="relative bg-[#0f172a] border border-white/10 rounded-2xl p-6 w-full max-w-md">
        <h3 className="text-xl font-bold text-white mb-4">{title}</h3>
        <p className="text-white/60 mb-6">{message}</p>
        <div className="flex justify-end gap-3">
          <Button onClick={onCancel}>{cancelText}</Button>
          <Button type={danger ? 'primary' : 'primary'} danger={danger} onClick={onConfirm}>
            {confirmText}
          </Button>
        </div>
      </div>
    </div>
  )
}

// 分页组件
interface PaginationInfo {
  current: number
  pageSize: number
  total: number
}

interface PaginationProps {
  info: PaginationInfo
  onChange: (page: number, pageSize: number) => void
}

export function Pagination({ info, onChange }: PaginationProps) {
  return (
    <div className="flex items-center justify-between mt-4">
      <span className="text-white/40 text-sm">
        共 {info.total} 条记录，第 {info.current}/{Math.ceil(info.total / info.pageSize)} 页
      </span>
      <div className="flex gap-2">
        <Button
          size="small"
          disabled={info.current <= 1}
          onClick={() => onChange(info.current - 1, info.pageSize)}
        >
          上一页
        </Button>
        <Button
          size="small"
          disabled={info.current >= Math.ceil(info.total / info.pageSize)}
          onClick={() => onChange(info.current + 1, info.pageSize)}
        >
          下一页
        </Button>
      </div>
    </div>
  )
}

// 搜索栏组件
interface SearchBarProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  onSearch?: () => void
}

export function SearchBar({ value, onChange, placeholder = '搜索...', onSearch }: SearchBarProps) {
  return (
    <div className="flex gap-2">
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && onSearch?.()}
        placeholder={placeholder}
        className="flex-1 px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/30 focus:border-purple-500 outline-none"
      />
      {onSearch && (
        <button
          onClick={onSearch}
          className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-xl"
        >
          搜索
        </button>
      )}
    </div>
  )
}

// 标签选择器
interface TagSelectorProps {
  value: string[]
  onChange: (tags: string[]) => void
  suggestions?: string[]
}

export function TagSelector({ value = [], onChange, suggestions = [] }: TagSelectorProps) {
  const [input, setInput] = useState('')

  const handleAdd = (tag: string) => {
    if (tag && !value.includes(tag)) {
      onChange([...value, tag])
    }
    setInput('')
  }

  const handleRemove = (tag: string) => {
    onChange(value.filter((t) => t !== tag))
  }

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-2">
        {value.map((tag) => (
          <span
            key={tag}
            className="inline-flex items-center gap-1 px-3 py-1 bg-purple-500/20 text-purple-300 rounded-full text-sm"
          >
            #{tag}
            <button onClick={() => handleRemove(tag)} className="hover:text-white">
              ×
            </button>
          </span>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ',') {
              e.preventDefault()
              handleAdd(input.trim())
            }
          }}
          placeholder="输入标签后按回车添加"
          className="flex-1 px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/30 focus:border-purple-500 outline-none"
        />
      </div>
      {suggestions.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {suggestions.slice(0, 5).map((s) => (
            <button
              key={s}
              onClick={() => handleAdd(s)}
              className="px-2 py-0.5 bg-white/5 hover:bg-white/10 text-white/40 text-xs rounded"
            >
              {s}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

import { useState } from 'react'