"use client";

import Layout from "@/app/components/Layout";
import Link from "next/link";

export default function PrivacyPage() {
  return (
    <Layout>
      <div className="pb-20">
        <section className="pt-8 pb-16 px-4">
          <div className="max-w-2xl mx-auto">
            <div className="mb-8">
              <h1 className="text-3xl md:text-4xl font-bold mb-4 bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent leading-tight">
                隐私政策（模板）
              </h1>
              <p className="text-sm text-gray-400">
                本页面为模板内容，请在上线前替换为正式版本。
              </p>
            </div>

            <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-100 mb-4">我们收集什么</h2>
              <ul className="space-y-2 text-gray-300 text-sm">
                <li>• 评估输入：行业、收入区间、雇员、POS、信号项</li>
                <li>• 付款信息：由 Stripe 处理，我们不存储银行卡信息</li>
                <li>• 技术信息：基础访问日志（用于安全与故障排查）</li>
              </ul>
            </div>

            <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-100 mb-4">我们如何使用数据</h2>
              <ul className="space-y-2 text-gray-300 text-sm">
                <li>• 生成风险评估与决策建议</li>
                <li>• 交付已购买内容（报告/解锁内容）</li>
                <li>• 改进产品质量与稳定性</li>
              </ul>
            </div>

            <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-100 mb-4">数据保存与第三方</h2>
              <ul className="space-y-2 text-gray-300 text-sm">
                <li>• 保存周期：默认 12 个月，或按法律要求保存更长时间</li>
                <li>• 第三方：Stripe（支付处理）</li>
              </ul>
              <p className="mt-3 text-xs text-gray-500">
                如需删除或导出数据，请联系：support@hispanocomply.com
              </p>
            </div>

            <div className="text-center">
              <Link
                href="/"
                className="inline-block bg-gradient-to-r from-purple-600 to-cyan-600 text-white font-semibold px-6 py-3 rounded-xl hover:from-purple-700 hover:to-cyan-700 transition-all"
              >
                返回首页
              </Link>
            </div>
          </div>
        </section>
      </div>
    </Layout>
  );
}
