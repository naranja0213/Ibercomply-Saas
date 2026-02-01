"use client";

import React from "react";
import { useRouter } from "next/navigation";
import Layout from "@/app/components/Layout";

const STAGES = [
  {
    value: "PRE_AUTONOMO",
    title: "我还没注册 Autónomo",
    description: "判断当前经营行为中，是否已经出现需要被留意的合规风险隐患点",
    icon: "📋",
  },
  {
    value: "AUTONOMO",
    title: "我已注册 Autónomo",
    description: "识别在当前经营阶段，哪些风险点正在累积，是否需要提前调整或升级结构",
    icon: "✅",
  },
  {
    value: "SL",
    title: "我已注册 SL 公司",
    description: "检查当前业务中，是否存在被忽略的高暴露风险点或材料薄弱环节",
    icon: "🏢",
  },
];

export default function AssessmentStartPage() {
  const router = useRouter();
  
  // ✅ 检查是否有 prefill_stage 参数（从复评按钮传入）
  const [prefilledStage, setPrefilledStage] = React.useState<string | null>(null);
  const hasProcessedPrefill = React.useRef(false);
  
  React.useEffect(() => {
    if (typeof window !== "undefined" && !hasProcessedPrefill.current) {
      const params = new URLSearchParams(window.location.search);
      const prefill = params.get("prefill_stage");
      // ✅ 只接受有效的 stage 值，防止异常值
      if (prefill && ["PRE_AUTONOMO", "AUTONOMO", "SL"].includes(prefill)) {
        setPrefilledStage(prefill);
        hasProcessedPrefill.current = true;
        // ✅ 立即清除 query 参数，防止循环跳转
        router.replace(window.location.pathname);
      }
    }
  }, [router]);

  const handleSelectStage = React.useCallback((stage: string) => {
    // 保存 stage 到 localStorage
    if (typeof window !== "undefined") {
      localStorage.setItem("assessment_stage", stage);
    }
    // 跳转到表单页（使用 replace 避免历史记录问题）
    router.replace("/assessment/form");
  }, [router]);
  
  // ✅ 如果有预填充的 stage，自动跳转（只执行一次）
  React.useEffect(() => {
    if (prefilledStage && hasProcessedPrefill.current) {
      handleSelectStage(prefilledStage);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [prefilledStage]); // 只依赖 prefilledStage，避免循环

  return (
    <Layout>
      <div className="pb-20">
        <section className="pt-8 pb-16 px-4">
          <div className="max-w-2xl mx-auto text-center mb-8">
            <h1 className="text-3xl md:text-4xl font-bold mb-6 bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent leading-tight">
              免费合规风险评估
            </h1>
            <p className="text-lg text-gray-300">
              选择您当前的经营身份，我们会为您提供对应的风险评估
            </p>
          </div>

          <div className="max-w-2xl mx-auto px-4 space-y-4">
            {STAGES.map((stage) => (
              <button
                key={stage.value}
                onClick={() => handleSelectStage(stage.value)}
                className="w-full text-left p-6 bg-slate-800/50 rounded-xl border border-slate-700 hover:border-purple-500/50 transition-all hover:bg-slate-800"
              >
                <div className="flex items-start gap-4">
                  <div className="text-4xl">{stage.icon}</div>
                  <div className="flex-1">
                    <h2 className="text-lg font-semibold text-gray-100 mb-1">
                      {stage.title}
                    </h2>
                    <p className="text-sm text-gray-400">{stage.description}</p>
                  </div>
                  <div className="text-gray-400">
                    <svg
                      className="w-6 h-6"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 5l7 7-7 7"
                      />
                    </svg>
                  </div>
                </div>
              </button>
            ))}
          </div>

          <div className="max-w-2xl mx-auto px-4 mt-8">
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <p className="text-sm text-gray-300">
                💡 <strong className="text-purple-400">提示：</strong>评估过程约 3 分钟，不收集身份信息，仅用于合规风险参考。
              </p>
            </div>
          </div>
        </section>
      </div>
    </Layout>
  );
}

