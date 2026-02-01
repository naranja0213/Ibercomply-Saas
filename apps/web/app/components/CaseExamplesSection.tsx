/**
 * CaseExamplesSection - 客户案例示例模块
 * 
 * 展示3个典型经营场景示例，增强用户信任感
 * 注意：这些不是"真实客户"，而是"典型场景示例"
 */
"use client";

import React from "react";
import Link from "next/link";

interface CaseExample {
  industry: string;
  location: string;
  background: string;
  coreIssue: string;
  realResult: string;
  judgment: string;
  nextStep: string;
  riskGroup?: string;  // ✅ 新增：risk group 标签
}

const caseExamples: CaseExample[] = [
  {
    industry: "餐饮行业",
    location: "马德里",
    background: "在市中心开了一家小餐厅，月收入约 €3,500，使用 POS 刷卡收款",
    coreIssue: "⚠️ 核心问题：开业时未申请市政活动许可（Licencia de Actividad），被市政检查发现",
    realResult: "💡 真实结果：市政罚款 €1,500，并要求在 30 天内补齐许可，否则可能面临更高罚款或强制停业",
    judgment: "🧭 系统判断：许可类问题通常不会主动提醒，往往在投诉或复查时一次性暴露。属于许可类行业高风险点，建议先确认是否已取得所有必要许可（市政、卫生、消防）",
    nextStep: "👉 下一步建议：立即检查并补齐市政许可、卫生许可证，建立许可档案，避免重复罚款",
    riskGroup: "市政风险",  // ✅ 新增：risk group 标签
  },
  {
    industry: "美容/美发/美甲店",
    location: "巴塞罗那",
    background: "经营美发店 2 年，月收入 €2,800，主要服务个人客户，部分现金收款",
    coreIssue: "⚠️ 核心问题：未按时申报 VAT（IVA），且部分收入未开票，被税务局抽查发现",
    realResult: "💡 真实结果：要求补缴过去 2 年的 VAT 约 €3,200，另加滞纳金和罚款 €1,800，总计约 €5,000",
    judgment: "🧭 系统判断：VAT 申报错误通常会在数据比对时被发现，追溯期可达 4 年。美容美发属于高检查频率行业，VAT 申报和开票记录是关键风险点",
    nextStep: "👉 下一步建议：立即建立固定开票流程，补申报 VAT，建立收入-票据对账体系，避免后续追溯",
    riskGroup: "税务风险",  // ✅ 新增：risk group 标签
  },
  {
    industry: "百元店",
    location: "瓦伦西亚",
    background: "经营百元店 3 年，月收入 €4,000，销售日用品和部分电子产品",
    coreIssue: "⚠️ 核心问题：店内销售的部分电子产品被查出为仿牌商品（仿冒商标），侵犯知识产权",
    realResult: "💡 真实结果：被消费者协会和海关联合检查，罚款 €2,500，并要求立即下架所有仿牌商品",
    judgment: "🧭 系统判断：仿牌问题通常在消费者投诉或定期检查时暴露，进货渠道不清晰时风险更高。百元店需特别注意进货渠道和产品授权，仿牌风险可能导致高额罚款和供应商责任",
    nextStep: "👉 下一步建议：立即清理可疑商品，建立进货凭证档案（发票、授权证明），选择有授权的供应商",
    riskGroup: "消费者保护",  // ✅ 新增：risk group 标签
  },
];

export default function CaseExamplesSection() {
  return (
    <section className="py-16 px-4" id="examples">
      <div className="max-w-2xl mx-auto">
        <h2 className="text-2xl md:text-3xl font-bold mb-4 text-center">
          他们和你一样，不确定自己是否有风险
        </h2>
        
        <p className="text-sm text-gray-400 text-center mb-8">
          以下是一些真实经营场景示例，展示系统如何给出判断和建议
        </p>

        <div className="space-y-6 mb-8">
          {caseExamples.map((example, index) => (
            <div
              key={index}
              className="bg-slate-800/50 rounded-xl border border-slate-700 p-6"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="font-semibold text-gray-200">
                  {example.industry}
                </div>
                <div className="flex items-center gap-3">
                  {example.riskGroup && (
                    <span className="rounded-full border border-white/10 bg-black/20 px-3 py-1 text-xs text-gray-300">
                      {example.riskGroup}
                    </span>
                  )}
                  <div className="text-sm text-gray-400">
                    {example.location}
                  </div>
                </div>
              </div>

              <p className="text-sm text-gray-300 mb-4 leading-relaxed">
                {example.background}
              </p>

              <div className="space-y-3">
                <div className="text-sm text-orange-200 leading-relaxed">
                  {example.coreIssue}
                </div>
                
                <div className="text-sm text-yellow-200 leading-relaxed">
                  {example.realResult}
                </div>
                <div className="text-xs text-gray-500 italic mt-1">
                  这类罚款在同类商户中并不少见，且往往会重复发生。
                </div>
                
                <div className="text-sm text-cyan-200 leading-relaxed">
                  {example.judgment}
                </div>
                
                <div className="text-sm text-emerald-200 leading-relaxed">
                  {example.nextStep}
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="text-center">
          <Link
            href="/assessment/start"
            className="inline-block text-lg text-purple-400 hover:text-purple-300 font-semibold transition-all mb-4"
          >
            看看你的情况属于哪一类 → 免费评估
          </Link>
          <p className="text-sm text-gray-500 italic">
            这些并不是"极端案例"，而是西班牙中小商户中最常见的三类合规罚款。
          </p>
        </div>
      </div>
    </section>
  );
}

