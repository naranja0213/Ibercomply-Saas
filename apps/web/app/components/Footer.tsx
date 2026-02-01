"use client";

import Link from "next/link";

export default function Footer() {
  return (
    <footer className="border-t border-slate-700 bg-slate-900/50 mt-auto">
      <div className="max-w-2xl mx-auto px-4 py-6">
        {/* 产品说明 */}
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-300 mb-3">关于本评估</h3>
          <p className="text-xs text-gray-400 leading-relaxed">
            IberComply 是一个面向在西班牙的华人个体经营者的合规风险评估工具。
            我们通过分析行业特点、收入规模、经营方式等因素，帮助您了解当前经营状态的合规风险等级。
          </p>
        </div>

        {/* 免责声明链接 */}
        <div className="pt-4 border-t border-slate-700">
          <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4 mb-4">
            <div className="flex items-start gap-3">
              <span className="text-xl">⚠️</span>
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-gray-300 mb-2">重要说明</h3>
                <p className="text-xs text-gray-400 leading-relaxed mb-2">
                  IberComply 并非西班牙税务局（Agencia Tributaria），也不隶属于任何政府机构。
                  本平台提供的是基于公开法规、行业经验和风险模型的合规风险评估与决策建议工具。
                </p>
                <Link
                  href="/legal/disclaimer"
                  className="text-xs text-purple-400 hover:text-purple-300 underline"
                >
                  查看完整免责声明 →
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* 复评入口标准句（规范要求） */}
        <div className="mt-6 pt-4 border-t border-slate-700">
          <p className="text-xs text-gray-400 text-center">
            你可以在经营状态发生变化时，随时进行一次新的复评。
          </p>
        </div>

        {/* 版权信息 */}
        <div className="mt-4 text-center">
          <p className="text-xs text-gray-500">
            © 2024 IberComply. 保留所有权利。
          </p>
        </div>
      </div>
    </footer>
  );
}

