import type { Metadata } from 'next'
import Script from 'next/script'
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
      <body>
        <Script
          src="https://www.googletagmanager.com/gtag/js?id=G-2M32D0V0R3"
          strategy="afterInteractive"
        />
        <Script id="ga4" strategy="afterInteractive">
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'G-2M32D0V0R3');
          `}
        </Script>
        {children}
      </body>
    </html>
  )
}

