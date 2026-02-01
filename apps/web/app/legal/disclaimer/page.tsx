"use client";

import Layout from "@/app/components/Layout";
import Link from "next/link";

export default function DisclaimerPage() {
  return (
    <Layout>
      <div className="pb-20">
        <section className="pt-8 pb-16 px-4">
          <div className="max-w-2xl mx-auto">
            {/* 标题 */}
            <div className="mb-8">
              <h1 className="text-3xl md:text-4xl font-bold mb-4 bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent leading-tight">
                免责声明
              </h1>
            </div>

            {/* 开篇说明 */}
            <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6 mb-6">
              <div className="space-y-4 text-gray-300 leading-relaxed">
                <p>
                  IberComply 是一个基于公开法规、行业经验和风险模型的合规风险评估与决策辅助工具，
                  旨在帮助用户理解其当前经营状态下可能存在的合规风险暴露点。
                </p>
              </div>
            </div>

            {/* 本工具能做什么 */}
            <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-100 mb-4">本工具能做什么</h2>
              <ul className="space-y-3 text-gray-300 leading-relaxed">
                <li className="flex items-start">
                  <span className="text-purple-400 mr-2">•</span>
                  <span>提示在不同经营阶段下，哪些问题更容易被关注</span>
                </li>
                <li className="flex items-start">
                  <span className="text-purple-400 mr-2">•</span>
                  <span>
                    帮助你判断：
                    <br />
                    <span className="ml-4 text-gray-400">👉 是否已经接近需要注册 Autónomo / SL 的阶段</span>
                    <br />
                    <span className="ml-4 text-gray-400">👉 哪些材料、流程、行为值得优先补齐</span>
                  </span>
                </li>
                <li className="flex items-start">
                  <span className="text-purple-400 mr-2">•</span>
                  <span>提供结构化行动建议，帮助你降低未来被追溯、被要求补材料或被检查的概率</span>
                </li>
              </ul>
            </div>

            {/* 本工具不能替代什么 */}
            <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-100 mb-4">本工具不能替代什么</h2>
              <div className="space-y-3 text-gray-300 leading-relaxed">
                <p>
                  请注意，IberComply 不提供：
                </p>
                <ul className="space-y-2 ml-4">
                  <li className="flex items-start">
                    <span className="text-red-400 mr-2">•</span>
                    <span>法律意见</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-red-400 mr-2">•</span>
                    <span>税务申报建议</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-red-400 mr-2">•</span>
                    <span>个案裁定或处罚结论</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-red-400 mr-2">•</span>
                    <span>既往未申报收入/现金的处理建议</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-red-400 mr-2">•</span>
                    <span>任何规避监管、逃税或洗钱的方案或操作指导</span>
                  </li>
                </ul>
                <p className="mt-4 text-gray-400">
                  如涉及历史合规问题，请咨询具备执业资格的律师或 gestor；本平台仅提供风险评估与材料准备框架。
                </p>
                <p className="mt-4 text-gray-400">
                  数字化服务一经交付不支持退款。
                </p>
                <p className="mt-4">
                  本平台 <strong className="text-gray-200">不是</strong> 西班牙税务局（Agencia Tributaria），
                  也不隶属于任何政府机构、律师事务所或 gestor 机构。
                </p>
              </div>
            </div>

            {/* 关于"风险分数"的说明 */}
            <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-100 mb-4">关于"风险分数"的说明（请勿误读）</h2>
              <div className="space-y-3 text-gray-300 leading-relaxed">
                <p>
                  报告中的风险分数用于反映：
                </p>
                <div className="ml-4 p-3 bg-purple-900/20 border border-purple-800/50 rounded-lg">
                  <p className="text-purple-300 font-medium">
                    当前经营状态的「合规暴露度」
                  </p>
                </div>
                <p className="mt-4">
                  它 <strong className="text-gray-200">不代表</strong>：
                </p>
                <ul className="space-y-2 ml-4">
                  <li className="flex items-start">
                    <span className="text-gray-500 mr-2">•</span>
                    <span>是否已经违法</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-gray-500 mr-2">•</span>
                    <span>是否一定会被罚款</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-gray-500 mr-2">•</span>
                    <span>是否已进入执法程序</span>
                  </li>
                </ul>
                <p className="mt-4 text-gray-400">
                  分数越高，表示在现实检查中 <strong className="text-gray-300">更可能被要求解释、补材料或调整结构</strong>。
                </p>
              </div>
            </div>

            {/* 关于评估结果的适用范围 */}
            <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-100 mb-4">关于评估结果的适用范围</h2>
              <div className="space-y-3 text-gray-300 leading-relaxed">
                <p>
                  本评估基于你填写的信息与评估当时的规则版本
                </p>
                <p>
                  如果你的以下情况发生变化，原评估可能不再适用：
                </p>
                <ul className="space-y-2 ml-4">
                  <li className="flex items-start">
                    <span className="text-yellow-400 mr-2">•</span>
                    <span>收入规模明显变化</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-yellow-400 mr-2">•</span>
                    <span>新增员工 / 外包</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-yellow-400 mr-2">•</span>
                    <span>新增 POS / 平台收款</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-yellow-400 mr-2">•</span>
                    <span>经营模式或行业发生变化</span>
                  </li>
                </ul>
                <div className="mt-4 p-3 bg-cyan-900/20 border border-cyan-800/50 rounded-lg">
                  <p className="text-cyan-300 text-sm">
                    📌 在这些情况下，我们建议你重新进行一次评估。
                  </p>
                </div>
              </div>
            </div>

            {/* 关于专业协助 */}
            <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-100 mb-4">关于专业协助</h2>
              <div className="space-y-3 text-gray-300 leading-relaxed">
                <p>
                  很多用户会在以下时机使用 IberComply：
                </p>
                <div className="ml-4 p-3 bg-purple-900/20 border border-purple-800/50 rounded-lg">
                  <p className="text-purple-300">
                    在联系 gestor、律师或顾问 <strong>之前</strong>，先确认「问题可能出在哪里」。
                  </p>
                </div>
                <p className="mt-4">
                  本工具可以帮助你：
                </p>
                <ul className="space-y-2 ml-4">
                  <li className="flex items-start">
                    <span className="text-purple-400 mr-2">•</span>
                    <span>更清楚地描述你的情况</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-purple-400 mr-2">•</span>
                    <span>更高效地与专业人士沟通</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-purple-400 mr-2">•</span>
                    <span>避免无方向地咨询或过度整改</span>
                  </li>
                </ul>
              </div>
            </div>

            {/* 最后说明 */}
            <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-100 mb-4">最后说明</h2>
              <div className="space-y-3 text-gray-300 leading-relaxed">
                <p>
                  本平台提供的内容仅用于风险提示与材料准备建议，不构成任何形式的法律、税务或财务意见。
                </p>
                <p className="text-gray-400">
                  如需正式结论或申报行为，请咨询具备执业资格的专业人士。
                </p>
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

