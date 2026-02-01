"use client";

import Layout from "@/app/components/Layout";
import Link from "next/link";

export default function TermsPage() {
  return (
    <Layout>
      <div className="pb-20">
        <section className="pt-8 pb-16 px-4">
          <div className="max-w-2xl mx-auto">
            <div className="mb-8">
              <h1 className="text-3xl md:text-4xl font-bold mb-4 bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent leading-tight">
                使用条款（模板）
              </h1>
              <p className="text-sm text-gray-400">
                本页面为模板内容，请在上线前替换为正式版本。
              </p>
            </div>

            <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-100 mb-4">服务定位</h2>
              <p className="text-sm text-gray-300 leading-relaxed">
                本平台提供合规风险评估与决策辅助，仅供参考，不构成法律或税务建议。
                如涉及历史问题或需要正式结论，请咨询专业人士。
              </p>
            </div>

            <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-100 mb-4">付款与交付</h2>
              <ul className="space-y-2 text-gray-300 text-sm">
                <li>• 付款通过 Stripe 完成</li>
                <li>• 解锁内容基于付款状态即时交付</li>
                <li>• 数字化服务一经交付不支持退款</li>
              </ul>
            </div>

            <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-100 mb-4">用户责任</h2>
              <ul className="space-y-2 text-gray-300 text-sm">
                <li>• 用户需保证输入信息真实有效</li>
                <li>• 本平台不对因误填导致的损失承担责任</li>
              </ul>
            </div>

            <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-100 mb-4">退款与权限回收</h2>
              <ul className="space-y-2 text-gray-300 text-sm">
                <li>• 数字化服务一经交付不支持退款</li>
                <li>• 若对扣款或交付有异议，请联系支持邮箱</li>
              </ul>
              <p className="mt-3 text-xs text-gray-500">
                支持邮箱：support@hispanocomply.com
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
