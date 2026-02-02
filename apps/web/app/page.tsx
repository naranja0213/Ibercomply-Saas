"use client";

import Link from "next/link";
import Layout from "./components/Layout";
import StickyCta from "./components/StickyCta";
import CaseExamplesSection from "./components/CaseExamplesSection";

export default function LandingPage() {
  return (
    <Layout>
      <div className="pb-20">
        {/* 屏 1（首屏）：一句话 + CTA */}
        <section className="relative pt-8 pb-16 px-4">
          <div className="max-w-2xl mx-auto text-center">
            <h1 className="text-3xl md:text-4xl font-bold mb-6 bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent leading-tight">
            伊贝合规风险评估与决策辅助平台,幫你判断处在哪个合规风险阶段
            </h1>
            
            <p className="text-lg text-gray-300 mb-8">
              约 3 分钟评估 → 输出 <span className="text-gray-100 font-semibold">A/B/C/D 风险阶段</span>、
              Top 3 <span className="text-gray-100 font-semibold">解释失败点</span>（解释难度/触发来源），以及
              <span className="text-gray-100 font-semibold">你现在最不该做的事</span>。
              <br />
              <span className="text-base text-gray-400">面向在西班牙经营的华人个体户与商户</span>
            </p>
            
            <Link
              href="/assessment/start"
              className="inline-block bg-gradient-to-r from-purple-600 to-cyan-600 text-white font-semibold px-8 py-4 rounded-xl hover:from-purple-700 hover:to-cyan-700 transition-all text-lg shadow-lg hover:shadow-xl mb-4"
            >
              👉 开始免费评估（约 3 分钟）
            </Link>
            <div className="mt-2 mx-auto max-w-xl text-xs text-gray-400 leading-relaxed">
              不填身份信息 · 可用区间填写 · 只做未来合规决策辅助（不提供既往未申报现金处理建议，不提供规避监管/逃税/洗钱指导）
            </div>
            <p className="mt-3 text-sm text-gray-300">
              <span className="font-semibold text-gray-100">合规风险评估与决策辅助平台</span>
              <span className="text-gray-400">（先自查，再决定要不要找 gestor/律师）</span>
            </p>
            <div className="mt-6 mx-auto max-w-xl rounded-xl border border-slate-700 bg-slate-800/40 p-4 text-left">
              <div className="text-xs text-gray-400 mb-2">评估完成后，你会得到：</div>
              <ul className="space-y-2 text-sm text-gray-200">
                <li>• 你的 <span className="font-semibold">A/B/C/D 风险阶段</span> 与阶段解释</li>
                <li>• Top 3 <span className="font-semibold">解释失败点</span>（解释难度 / 常见触发来源（用于理解风险））</li>
                <li>• <span className="font-semibold">最不该做的事</span>（避免把可控问题升级）</li>
                <li>• 解锁后可下载 <span className="font-semibold">PDF 报告</span> + 行动/材料清单</li>
              </ul>
            </div>
          </div>
        </section>

        {/* 屏 2（痛点）：你是不是遇到这些（对号列表）+ CTA */}
        <section className="py-16 px-4 bg-slate-800/50" id="who">
          <div className="max-w-2xl mx-auto">
            <h2 className="text-2xl md:text-3xl font-bold mb-4 text-center">
              很多人不是不想合规，是不知道什么时候该开始
            </h2>
            
            <div className="bg-yellow-900/20 border border-yellow-800/50 rounded-xl p-4 mb-6">
              <p className="text-sm text-yellow-200 leading-relaxed">
                “我只是先试试，还不算生意吧？”<br />
                “朋友也没注册，好像也没事？”<br />
                “再等等，看以后收入稳不稳定？”
              </p>
              <p className="text-sm text-yellow-300 mt-2 font-semibold">
                👉 问题是：很多风险不会提前提醒，往往是在“被问到/被对比”时才突然变得难以解释
              </p>
            </div>
            
            <h3 className="text-xl font-semibold mb-6 text-center text-gray-300">
              如果你擔心或者已經遇到这些問題，建议先评估一次：
            </h3>
            
            <div className="bg-slate-800 rounded-xl p-6 mb-6 border border-slate-700">
              <ul className="space-y-4">
                <li className="flex items-start">
                  <span className="text-purple-400 mr-3 text-xl">✓</span>
                  <span className="text-gray-300">银行要求解释资金来源/现金存入原因</span>
                </li>
                <li className="flex items-start">
                  <span className="text-purple-400 mr-3 text-xl">✓</span>
                  <span className="text-gray-300">Gestor 提到“IVA 有点低”或“申报数据不太对”</span>
                </li>
                <li className="flex items-start">
                  <span className="text-purple-400 mr-3 text-xl">✓</span>
                  <span className="text-gray-300">听说同行被查，担心会倒查多年</span>
                </li>
                <li className="flex items-start">
                  <span className="text-purple-400 mr-3 text-xl">✓</span>
                  <span className="text-gray-300">想把店转让 / 贷款 / 融资，但账务不够“可解释”</span>
                </li>
                <li className="flex items-start">
                  <span className="text-purple-400 mr-3 text-xl">✓</span>
                  <span className="text-gray-300">家里人开始担心风险（房子、孩子、配偶）</span>
                </li>
              </ul>
            </div>
            
            <div className="text-center">
              <Link
                href="/assessment/start"
                className="inline-block bg-gradient-to-r from-purple-600 to-cyan-600 text-white font-semibold px-8 py-4 rounded-xl hover:from-purple-700 hover:to-cyan-700 transition-all text-lg shadow-lg"
              >
                👉 开始免费评估（约 3 分钟）
              </Link>
              <p className="text-xs text-gray-500 mt-3">
                数字化服务一经交付不支持退款
              </p>
            </div>
          </div>
        </section>

        {/* 屏 3（价值）：你解决了什么 */}
        <section className="py-16 px-4" id="value">
          <div className="max-w-2xl mx-auto">
            <h2 className="text-2xl md:text-3xl font-bold mb-6 text-center">
              IberComply 伊贝合规帮你在出事前看清风险
            </h2>
            
            <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6 mb-6">
              <ul className="space-y-3 text-gray-300">
                <li className="flex items-start">
                  <span className="text-green-400 mr-2 text-xl">✓</span>
                  <span>输出 A/B/C/D 风险阶段（可解释 → 高可见性 → 触发点临近 → 需专业介入）</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-400 mr-2 text-xl">✓</span>
                  <span>标出 Top 3 解释失败点（解释难度 + 常见触发来源）</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-400 mr-2 text-xl">✓</span>
                  <span>给出“你现在最不该做的 3 件事”（避免把可控问题升级）</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-400 mr-2 text-xl">✓</span>
                  <span>生成 PDF 报告：摘要 + 行动清单 + 材料清单 </span>
                </li>
              </ul>
            </div>

            {/* A/B/C/D 阶段小卡 */}
            <div className="mb-6">
              <div className="text-xs text-gray-400 mb-2">阶段说明（示意）：</div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4">
                <div className="text-sm font-semibold text-emerald-200">阶段 A：可解释但需注意</div>
                <div className="mt-2 text-xs text-gray-300">
                  可解释性较高，风险整体可控，重点是保持记录连续性。
                </div>
              </div>
              <div className="rounded-xl border border-yellow-500/30 bg-yellow-500/10 p-4">
                <div className="text-sm font-semibold text-yellow-200">阶段 B：高可见性（容易被注意）</div>
                <div className="mt-2 text-xs text-gray-300">
                  更容易被对比与提问，材料链需要系统化与持续补齐。
                </div>
              </div>
              <div className="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
                <div className="text-sm font-semibold text-orange-200">阶段 C：触发点临近</div>
                <div className="mt-2 text-xs text-gray-300">
                  触发概率明显上升，拖延会增加解释与沟通成本。
                </div>
              </div>
              <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4">
                <div className="text-sm font-semibold text-red-200">阶段 D：需要专业介入</div>
                <div className="mt-2 text-xs text-gray-300">
                  暴露面较高，建议尽快引入专业人士判断与整改优先级。
                </div>
              </div>
              </div>
            </div>
            
            <div className="bg-purple-900/20 border border-purple-800/50 rounded-xl p-4 mb-6">
              <p className="text-sm text-gray-300 leading-relaxed">
                <strong className="text-purple-300">方法说明：</strong>基于公开规则与常见监管关注点构建，按“可解释性”视角帮助你做决策。
                我们不是税务局，也不替代律师/gestor。
              </p>
            </div>
            
            <div className="text-center">
              <Link
                href="/assessment/start"
                className="inline-block bg-gradient-to-r from-purple-600 to-cyan-600 text-white font-semibold px-8 py-4 rounded-xl hover:from-purple-700 hover:to-cyan-700 transition-all text-lg shadow-lg"
              >
                👉 开始免费评估（约 3 分钟）
              </Link>
            </div>
          </div>
        </section>

        {/* 屏 3.5（案例示例）：客户案例示例模块 */}
        <CaseExamplesSection />

        {/* 屏 4（信任）：会/不会做什么（左右对比）+ CTA */}
        <section className="py-16 px-4 bg-slate-800/50" id="how">
          <div className="max-w-2xl mx-auto">
            <h2 className="text-2xl md:text-3xl font-bold mb-8 text-center">
              这个评估会 / 不会做什么？
            </h2>
            
            <div className="grid md:grid-cols-2 gap-6 mb-8">
              {/* 会做什么 */}
              <div className="bg-green-900/20 border border-green-800/50 rounded-xl p-6">
                <h3 className="text-lg font-bold text-green-400 mb-4 flex items-center">
                  <span className="mr-2">✓</span>
                  这个评估会：
                </h3>
                <ul className="space-y-3 text-gray-300 text-sm">
                  <li className="flex items-start">
                    <span className="text-green-400 mr-2">•</span>
                    <span>输出 A/B/C/D 风险阶段与阶段解释</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-400 mr-2">•</span>
                    <span>标出 Top 3 解释失败点（解释难度/触发来源）</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-400 mr-2">•</span>
                    <span>给出“你现在最不该做的事”</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-400 mr-2">•</span>
                    <span>提供行动清单与材料准备框架（解锁后）</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-400 mr-2">•</span>
                    <span>生成可交付的 PDF 报告（解锁后）</span>
                  </li>
                </ul>
              </div>

              {/* 不会做什么 */}
              <div className="bg-red-900/20 border border-red-800/50 rounded-xl p-6">
                <h3 className="text-lg font-bold text-red-400 mb-4 flex items-center">
                  <span className="mr-2">✗</span>
                  这个评估不会：
                </h3>
                <ul className="space-y-3 text-gray-300 text-sm">
                  <li className="flex items-start">
                    <span className="text-red-400 mr-2">•</span>
                    <span>替代专业的法律或税务建议</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-red-400 mr-2">•</span>
                    <span>不要求实名；仅为提供服务与支付交付保留最小必要数据（符合隐私规范）</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-red-400 mr-2">•</span>
                    <span>不要求提供身份证/银行账户等敏感信息（支持用区间信息完成评估）</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-red-400 mr-2">•</span>
                    <span>提供任何关于既往未申报收入/现金的处理建议</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-red-400 mr-2">•</span>
                    <span>提供任何规避监管、逃税或洗钱的方案或操作指导</span>
                  </li>
                </ul>
              </div>
            </div>

            {/* 我们怎么判断 */}
            <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 mb-8">
              <h3 className="text-lg font-bold mb-4">我们怎么判断</h3>
              <p className="text-gray-300 mb-4">
                我们不问隐私，只看经营信号：
              </p>
              <div className="flex flex-wrap gap-2">
                <span className="px-3 py-1 bg-purple-900/50 text-purple-300 rounded-lg text-sm">行业</span>
                <span className="px-3 py-1 bg-cyan-900/50 text-cyan-300 rounded-lg text-sm">收入</span>
                <span className="px-3 py-1 bg-purple-900/50 text-purple-300 rounded-lg text-sm">雇员</span>
                <span className="px-3 py-1 bg-cyan-900/50 text-cyan-300 rounded-lg text-sm">POS</span>
              </div>
            </div>
            
            <div className="text-center">
              <Link
                href="/assessment/start"
                className="inline-block bg-gradient-to-r from-purple-600 to-cyan-600 text-white font-semibold px-8 py-4 rounded-xl hover:from-purple-700 hover:to-cyan-700 transition-all text-lg shadow-lg"
              >
                开始免费评估（约 3 分钟）
              </Link>
              <div className="mt-3 text-xs text-gray-500">
                <Link href="/legal/privacy" className="text-purple-400 hover:text-purple-300 underline">
                  隐私政策
                </Link>
                <span className="text-gray-600 mx-2">·</span>
                <Link href="/legal/terms" className="text-purple-400 hover:text-purple-300 underline">
                  使用条款
                </Link>
              </div>
            </div>
          </div>
        </section>
      </div>

      {/* 移动端 Sticky CTA */}
      <StickyCta />
    </Layout>
  );
}
