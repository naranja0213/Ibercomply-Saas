import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'IberComply - 伊贝合规风险评估助手',
  description: '西班牙华人 Autónomo 合规风险评估',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  )
}

