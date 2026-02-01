"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

export default function StickyCta() {
  const [visible, setVisible] = useState(false);
  const [nearFooter, setNearFooter] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const scrollY = window.scrollY;
      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight;

      // 显示条件：滚动超过 200px
      setVisible(scrollY > 200);

      // 隐藏条件：接近 Footer（距离底部小于 300px）
      const distanceToBottom = documentHeight - (scrollY + windowHeight);
      setNearFooter(distanceToBottom < 300);
    };

    window.addEventListener("scroll", handleScroll);
    handleScroll(); // 初始检查

    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  if (!visible || nearFooter) {
    return null;
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 z-40 md:hidden safe-bottom">
      <div className="max-w-2xl mx-auto px-4 pb-4">
        <Link
          href="/assessment/start"
          className="block w-full bg-gradient-to-r from-purple-600 to-cyan-600 text-white font-semibold py-4 px-6 rounded-xl hover:from-purple-700 hover:to-cyan-700 transition-all text-center shadow-lg"
        >
          <div className="text-lg">开始免费评估（约 3 分钟）</div>
          <div className="text-xs opacity-90 mt-1">不填身份信息 · 可用区间填写</div>
        </Link>
      </div>
    </div>
  );
}

