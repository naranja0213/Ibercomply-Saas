"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Layout from "@/app/components/Layout";
import IndustryGrid from "../components/IndustryGrid";
import Stepper from "../components/Stepper";
import Switch from "../components/Switch";
import SignalsPanel from "../components/SignalsPanel";
import { INDUSTRIES, INCOME_OPTIONS, INDUSTRY_SIGNALS, COMMON_SIGNALS, INCOME_PRESETS_BY_STAGE, getSliderConfig, getIncomeBandLabel } from "../constants";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export default function AssessmentFormPage() {
  const router = useRouter();
  const [stage, setStage] = useState<string | null>(null);
  const [industry, setIndustry] = useState("");
  const [monthlyIncome, setMonthlyIncome] = useState<number | null>(null);
  const [employeeCount, setEmployeeCount] = useState(0);
  const [hasPos, setHasPos] = useState(false);
  const [signals, setSignals] = useState<Record<string, boolean>>({});
  const [loading, setLoading] = useState(false);

  // 从 localStorage 读取 stage
  useEffect(() => {
    if (typeof window !== "undefined") {
      const savedStage = localStorage.getItem("assessment_stage");
      if (!savedStage) {
        // 如果没有 stage，跳转到 start 页
        router.push("/assessment/start");
      } else {
        setStage(savedStage);
      }
    }
  }, [router]);

  const [showIncomeAdjustToast, setShowIncomeAdjustToast] = useState(false);
  const [incomeAdjustMessage, setIncomeAdjustMessage] = useState("");

  // 当 stage 变化时，调整 monthlyIncome 到合法范围（带用户提示）
  useEffect(() => {
    if (stage && monthlyIncome !== null) {
      const slider = getSliderConfig(stage);
      let adjusted = false;
      let message = "";
      
      if (monthlyIncome > slider.max) {
        setMonthlyIncome(slider.max);
        adjusted = true;
        message = `已根据阶段调整收入范围，上限为 €${slider.max.toLocaleString()}`;
      }
      if (monthlyIncome < slider.min) {
        setMonthlyIncome(slider.min);
        adjusted = true;
        message = `已根据阶段调整收入范围，下限为 €${slider.min.toLocaleString()}`;
      }
      
      if (adjusted) {
        setIncomeAdjustMessage(message);
        setShowIncomeAdjustToast(true);
        // 3秒后自动隐藏
        setTimeout(() => setShowIncomeAdjustToast(false), 3000);
      }
    }
  }, [stage]); // eslint-disable-line react-hooks/exhaustive-deps

  // 获取当前行业对应的 signals
  const currentIndustrySignals = industry ? INDUSTRY_SIGNALS[industry] || [] : [];
  const allSignals = [...currentIndustrySignals, ...COMMON_SIGNALS];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!industry || monthlyIncome === null || !stage) {
      alert("请填写完整信息");
      return;
    }

    setLoading(true);
    
    // 保存表单数据到 sessionStorage（用于支付回调后重新请求）
    const formData = {
      stage,
      industry,
      monthly_income: monthlyIncome,
      employee_count: employeeCount,
      has_pos: hasPos,
      signals,
    };
    sessionStorage.setItem("assessment_input", JSON.stringify(formData));

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/compliance/assess`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          stage, // 添加 stage 字段
          industry,
          monthly_income: monthlyIncome,
          employee_count: employeeCount,
          has_pos: hasPos,
          signals,
        }),
      });

      if (!response.ok) {
        throw new Error("评估失败");
      }

      const data = await response.json();
      
      // 关键：assessment_id 只能来自 POST /assess 返回的 id
      if (!data.id) {
        throw new Error("后端未返回 assessment_id");
      }
      
      // 保存后端返回的 assessment_id（这是唯一权威来源）
      sessionStorage.setItem("assessment_id", data.id);
      
      // 将结果数据和原始表单数据存储到 sessionStorage，然后跳转到结果页
      sessionStorage.setItem("assessment_result", JSON.stringify(data));
      sessionStorage.setItem("assessment_input", JSON.stringify({
        stage,
        industry,
        monthly_income: monthlyIncome,
        employee_count: employeeCount,
        has_pos: hasPos,
        signals,
      }));
      sessionStorage.setItem("assessment_unlocked_tier", "none");
      router.push("/assessment/result");
    } catch (error) {
      console.error("Error:", error);
      alert("评估失败，请检查后端服务是否运行");
      setLoading(false);
    }
  };

  // 如果 stage 还未加载，显示加载状态
  if (!stage) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-gray-400">加载中...</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="pb-24">
        {/* 页面标题 */}
        <div className="bg-slate-800/50 border-b border-slate-700">
          <div className="max-w-2xl mx-auto px-4 py-6">
            <h1 className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
              免费合规风险评估
            </h1>
            <p className="text-sm text-gray-400 mt-2">快速评估您在西班牙的合规风险</p>
          </div>
        </div>

        <div className="max-w-2xl mx-auto px-4 py-6 space-y-6">
          {/* 流程条 */}
          <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2 flex-1">
                <div className="w-8 h-8 rounded-full bg-purple-600 text-white flex items-center justify-center font-bold text-sm flex-shrink-0">
                  1
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-semibold text-gray-300">填 5 项信息</div>
                  <div className="text-xs text-gray-500">行业、收入、雇员、POS、细节</div>
                </div>
              </div>
              <div className="w-8 h-0.5 bg-slate-600 mx-2"></div>
              <div className="flex items-center gap-2 flex-1">
                <div className="w-8 h-8 rounded-full bg-slate-600 text-gray-400 flex items-center justify-center font-bold text-sm flex-shrink-0">
                  2
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-semibold text-gray-400">生成风险阶段</div>
                  <div className="text-xs text-gray-500">约 3 分钟出结果</div>
                </div>
              </div>
              <div className="w-8 h-0.5 bg-slate-600 mx-2"></div>
              <div className="flex items-center gap-2 flex-1">
                <div className="w-8 h-8 rounded-full bg-slate-600 text-gray-400 flex items-center justify-center font-bold text-sm flex-shrink-0">
                  3
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-semibold text-gray-400">解锁行动清单</div>
                  <div className="text-xs text-gray-500">可选（€15）</div>
                </div>
              </div>
            </div>
          </div>
          
          {/* 表单区 */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 行业选择 */}
            
            <div>
              <label className="block text-sm font-medium mb-3 text-gray-300">您的行业</label>
              <p className="text-xs text-gray-400 mb-3 leading-relaxed">
                找不到完全匹配？请选择最接近的类型。我们会结合你后续的经营信号做评估。
              </p>
              <div className="max-h-[55vh] overflow-y-auto pr-2 overscroll-contain scrollbar-thin">
                <IndustryGrid industries={INDUSTRIES} value={industry} onChange={setIndustry} />
              </div>
            </div>

            {/* 月收入 */}
            <div>
              <div className="flex items-center gap-2 mb-2">
                <label className="block text-sm font-medium text-gray-300">月收入（€）</label>
                {stage === "PRE_AUTONOMO" && (
                  <span className="text-xs text-gray-400 bg-slate-700/50 px-2 py-0.5 rounded">
                    未稳定也没关系
                  </span>
                )}
              </div>
              <p className="text-xs text-gray-400 mb-3 leading-relaxed">
                不确定选哪个？滑动到最接近的数字即可（后续还会结合行业细项判断）。
              </p>
              
              <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-end justify-between gap-3 mb-4">
                  <div className="text-2xl font-semibold text-white">
                    €{monthlyIncome ?? 0}
                  </div>
                  <div className="text-xs text-gray-400 text-right">
                    {getIncomeBandLabel(monthlyIncome ?? 0)}
                  </div>
                </div>

                {(() => {
                  const slider = getSliderConfig(stage);
                  const presets = INCOME_PRESETS_BY_STAGE[stage || "AUTONOMO"] ?? INCOME_PRESETS_BY_STAGE.AUTONOMO;
                  
                  return (
                    <>
                      <input
                        type="range"
                        min={slider.min}
                        max={slider.max}
                        step={slider.step}
                        value={monthlyIncome ?? 0}
                        onChange={(e) => setMonthlyIncome(Number(e.target.value))}
                        className="w-full accent-violet-500"
                      />

                      <div className="mt-4 grid grid-cols-3 gap-2 sm:grid-cols-9">
                        {presets.map((v) => {
                          const active = monthlyIncome === v;
                          return (
                            <button
                              key={v}
                              type="button"
                              onClick={() => setMonthlyIncome(v)}
                              className={[
                                "rounded-xl px-3 py-2 text-xs font-medium transition border",
                                active
                                  ? "bg-violet-600 text-white border-transparent"
                                  : "bg-white/5 text-gray-200 hover:bg-white/10 border-white/10",
                              ].join(" ")}
                            >
                              €{v}
                            </button>
                          );
                        })}
                      </div>
                    </>
                  );
                })()}
              </div>
              
              {/* 收入范围调整提示 */}
              {showIncomeAdjustToast && (
                <div className="mt-3 rounded-lg bg-blue-500/20 border border-blue-500/30 px-4 py-2 text-xs text-blue-200">
                  {incomeAdjustMessage}
                </div>
              )}
            </div>

            {/* 雇员人数 */}
            <Stepper
              label="雇员人数"
              value={employeeCount}
              onChange={setEmployeeCount}
              min={0}
              max={10}
            />

            {/* POS */}
            <Switch label="是否使用 POS 刷卡机" checked={hasPos} onCheckedChange={setHasPos} />

            {/* Signals 面板 */}
            {industry && allSignals.length > 0 && (
              <SignalsPanel
                signals={allSignals}
                values={signals}
                onChange={(key, value) => setSignals((prev) => ({ ...prev, [key]: value }))}
              />
            )}
          </form>
        </div>

        {/* 底部固定按钮 */}
        <div className="fixed bottom-0 left-0 right-0 bg-slate-900/95 backdrop-blur-sm border-t border-slate-700 p-4 safe-bottom z-40">
          <div className="max-w-2xl mx-auto">
            <button
              onClick={(e) => {
                e.preventDefault();
                handleSubmit(e);
              }}
              disabled={loading || !industry || monthlyIncome === null}
              className="w-full bg-gradient-to-r from-purple-600 to-cyan-600 text-white font-semibold py-4 rounded-xl hover:from-purple-700 hover:to-cyan-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed text-lg"
            >
              {loading ? "评估中..." : "生成我的风险阶段（约 3 分钟）"}
            </button>
          </div>
        </div>
      </div>
    </Layout>
  );
}

