"use client";

import Layout from "../components/Layout";
import Link from "next/link";

export default function PartnersPage() {
  return (
    <Layout>
      <div className="pb-20">
        <section className="pt-8 pb-16 px-4">
          <div className="max-w-2xl mx-auto">
            {/* 标题 */}
            <div className="mb-8">
              <h1 className="text-3xl md:text-4xl font-bold mb-4 bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent leading-tight">
                关于合作
              </h1>
            </div>

            {/* 定位说明 */}
            <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6 mb-6">
              <div className="space-y-4 text-gray-300 leading-relaxed">
                <p>
                  IberComply 是一个合规风险评估与决策辅助工具，定位为<strong className="text-purple-400">正式咨询前的风险结构识别工具</strong>。
                </p>
                <p>
                  本平台 <strong className="text-gray-200">不是</strong> 西班牙税务局（Agencia Tributaria），<strong className="text-gray-200">不是</strong> 律师事务所，也<strong className="text-gray-200">不替代</strong> 任何专业服务。
                </p>
                <p className="text-gray-400">
                  我们的目标是在用户联系 Gestoría 或律师之前，帮助其更清楚地识别风险结构，从而提升后续咨询的效率。
                </p>
              </div>
            </div>

            {/* 当前状态 */}
            <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-100 mb-4">当前状态</h2>
              <div className="space-y-3 text-gray-300 leading-relaxed">
                <p>
                  面向 Gestoría、律师事务所等专业机构的合作功能仍在设计中，尚未正式开放。
                </p>
                <p className="text-gray-400 text-sm">
                  我们正在谨慎规划合作模式，确保既能服务用户需求，又能与专业机构的服务形成互补而非替代关系。
                </p>
              </div>
            </div>

            {/* 未来方向（占位说明） */}
            <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-100 mb-4">未来方向</h2>
              <div className="space-y-3 text-gray-300 leading-relaxed text-sm">
                <p>
                  我们理解专业机构对合规风险评估工具的需求，但目前不承诺任何具体功能或时间表。
                </p>
                <p className="text-gray-400">
                  如果未来有合适的合作模式，我们会优先考虑与具备良好服务口碑的专业机构进行对接。
                </p>
              </div>
            </div>

            {/* 联系方式（占位） */}
            <div className="bg-purple-900/20 rounded-xl border border-purple-800/50 p-6 mb-6">
              <h2 className="text-lg font-semibold text-purple-300 mb-3">联系方式</h2>
              <div className="space-y-3 text-gray-300 leading-relaxed">
                <p className="text-sm">
                  如果你希望推荐可信的 Gestor 或律师，或希望在未来合作功能开放时收到通知，欢迎通过以下方式联系：
                </p>
                <div className="mt-4">
                  <a
                    href="mailto:ibercomply@gmail.com"
                    className="text-purple-400 hover:text-purple-300 underline text-sm"
                  >
                    ibercomply@gmail.com
                  </a>
                </div>
              </div>
            </div>

            {/* 返回按钮 */}
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
