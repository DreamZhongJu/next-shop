import type { Metadata } from "next"
import "../styles/globals.css"
import '../styles/markdown.css'
import ChatWidget from "@/components/common/ChatWidget"
import Navigation from "@/components/home/Navigation"
import SidebarLayout from "@/components/sideBar"

export const metadata: Metadata = {
  title: "NextShop 电商平台",
  description: "一个使用 Next.js 和 Gin 开发的电商平台",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="zh-CN">
      <head>
        {/* ✅ 使用国内 CDN 加载通用字体（可选） */}
        <link
          rel="stylesheet"
          href="https://fonts.loli.net/css2?family=Inter:wght@400;600&display=swap"
        />
        {/* ❌ 不加载 favicon.ico，防止报错 */}
        {/* <link rel="icon" href="/favicon.ico" /> */}
      </head>
      <body className="antialiased font-sans bg-white text-black">
        <Navigation />
        <ChatWidget /> {/* ✅ 这里全局加载 AI 对话 */}
        {/* 页面主体 */}
        <main className="flex-1">
          {children}
        </main>
        <SidebarLayout />
      </body>
    </html>
  )
}
