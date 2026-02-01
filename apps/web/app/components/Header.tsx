"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Header() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const pathname = usePathname();

  const scrollToSection = (sectionId: string) => {
    setDrawerOpen(false);
    if (pathname === "/") {
      const element = document.getElementById(sectionId);
      if (element) {
        element.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    } else {
      window.location.href = `/#${sectionId}`;
    }
  };

  return (
    <>
      <header className="sticky top-0 z-50 bg-slate-900/95 backdrop-blur-sm border-b border-slate-700 safe-top">
        <div className="max-w-2xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            {/* Logo + 定位 */}
            <Link href="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-cyan-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">HC</span>
              </div>
              <div>
                <div className="text-lg font-bold bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent leading-tight">
                  IberComply
                </div>
                <div className="text-xs text-gray-400 leading-tight hidden sm:block">
                  伊贝合规风险评估助手
                </div>
              </div>
            </Link>
            
            {/* 右侧：CTA + 菜单 */}
            <div className="flex items-center gap-2">
              <Link
                href="/assessment/start"
                className="px-3 py-1.5 bg-gradient-to-r from-purple-600 to-cyan-600 text-white font-semibold rounded-lg hover:from-purple-700 hover:to-cyan-700 transition-all text-sm whitespace-nowrap"
              >
                免费评估
              </Link>
              
              {/* 菜单按钮 */}
              <button
                onClick={() => setDrawerOpen(true)}
                className="p-2 text-gray-400 hover:text-white transition-colors"
                aria-label="打开菜单"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* 信任条 */}
        <div className="bg-slate-800/50 border-t border-slate-700/50">
          <div className="max-w-2xl mx-auto px-4 py-2">
            <p className="text-xs text-gray-400 text-center">
              不需要身份证 · 不保存个人信息 · 仅做风险参考
            </p>
          </div>
        </div>
      </header>

      {/* Drawer 菜单 */}
      {drawerOpen && (
        <>
          {/* 背景遮罩 */}
          <div
            className="fixed inset-0 bg-black/50 z-50"
            onClick={() => setDrawerOpen(false)}
          />
          
          {/* Drawer 内容 */}
          <div className="fixed right-0 top-0 bottom-0 w-64 bg-slate-900 border-l border-slate-700 z-50 overflow-y-auto safe-top safe-bottom">
            <div className="p-4">
              {/* 关闭按钮 */}
              <div className="flex justify-end mb-6">
                <button
                  onClick={() => setDrawerOpen(false)}
                  className="p-2 text-gray-400 hover:text-white transition-colors"
                  aria-label="关闭菜单"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* 菜单项 */}
              <nav className="space-y-1">
                <Link
                  href="/assessment/start"
                  onClick={() => setDrawerOpen(false)}
                  className="block px-4 py-3 rounded-lg hover:bg-slate-800 transition-colors text-gray-300 hover:text-white"
                >
                  <div className="font-semibold">免费评估（约 3 分钟）</div>
                  <div className="text-xs text-gray-500 mt-1">快速了解风险阶段</div>
                </Link>

                <button
                  onClick={() => scrollToSection("who")}
                  className="w-full text-left px-4 py-3 rounded-lg hover:bg-slate-800 transition-colors text-gray-300 hover:text-white"
                >
                  <div className="font-semibold">适合谁用</div>
                  <div className="text-xs text-gray-500 mt-1">解决"我是不是该点"的焦虑</div>
                </button>

                <button
                  onClick={() => scrollToSection("how")}
                  className="w-full text-left px-4 py-3 rounded-lg hover:bg-slate-800 transition-colors text-gray-300 hover:text-white"
                >
                  <div className="font-semibold">我们怎么判断</div>
                  <div className="text-xs text-gray-500 mt-1">建立专业感</div>
                </button>

                <button
                  onClick={() => scrollToSection("disclaimer")}
                  className="w-full text-left px-4 py-3 rounded-lg hover:bg-slate-800 transition-colors text-gray-300 hover:text-white"
                >
                  <div className="font-semibold">免责声明</div>
                  <div className="text-xs text-gray-500 mt-1">风险防火墙</div>
                </button>

                <Link
                  href="/partners"
                  onClick={() => setDrawerOpen(false)}
                  className="block px-4 py-3 rounded-lg hover:bg-slate-800 transition-colors text-gray-300 hover:text-white"
                >
                  <div className="font-semibold">合作/对接</div>
                  <div className="text-xs text-gray-500 mt-1">Gestoría/律师/专业机构</div>
                </Link>
              </nav>
            </div>
          </div>
        </>
      )}
    </>
  );
}

