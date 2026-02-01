/**
 * ExpertPartnersPlaceholder - 合作顾问占位组件
 * 
 * 当前版本：纯占位展示，不提供真实服务、不跳转、不采集信息
 * 未来版本：可能会扩展为展示合作顾问列表或预约入口
 */
"use client";

import React from "react";

export default function ExpertPartnersPlaceholder() {
  return (
    <div className="mt-6 bg-slate-800/50 rounded-xl border border-slate-700 p-5">
      <div className="flex items-start gap-3">
        <span className="text-xl">ℹ️</span>
        <div className="flex-1">
          <div className="font-semibold text-gray-200 mb-2">
            需要专业人士介入时（可选）
          </div>
          <div className="text-sm text-gray-400 leading-relaxed space-y-2">
            <p>
              我们正在筛选合作顾问。
            </p>
            <p>
              如果你希望推荐可信的 gestor 或律师，欢迎联系我们。
            </p>
            <p className="text-xs text-gray-500 italic">
              本平台不提供法律或税务服务，是否联系第三方完全由用户自行决定。
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

