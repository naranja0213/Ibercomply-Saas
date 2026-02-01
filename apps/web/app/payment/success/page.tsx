"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Layout from "@/app/components/Layout";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

// 标准化 tier 字符串（处理各种可能的格式）
function normalizeTier(t: string | null | undefined): "none" | "basic_15" | "expert_39" {
  if (!t) return "none";
  const s = t.toLowerCase().trim();
  if (s.includes("expert") || s.includes("39")) return "expert_39";
  if (s.includes("basic") || s.includes("15")) return "basic_15";
  return "none";
}

export default function PaymentSuccessPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("正在验证支付状态...");

  useEffect(() => {
    const sessionId = searchParams.get("session_id");
    
    if (!sessionId) {
      setStatus("error");
      setMessage("缺少支付会话 ID");
      setTimeout(() => {
        router.replace("/assessment/start");
      }, 2000);
      return;
    }

    // 验证支付状态（带重试机制，等待 webhook 完成）
    const verifyPayment = async (retryCount = 0) => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/payment/status?session_id=${sessionId}`, {
          cache: "no-store",
        });
        
        if (!response.ok) {
          throw new Error("支付验证失败");
        }

        const data = await response.json();
        
        console.log(`[支付验证] 第 ${retryCount + 1} 次尝试：`, {
          paid: data.paid,
          assessment_id: data.assessment_id,
          unlocked_tier: data.unlocked_tier,
        });

        // ✅ 如果支付成功但 unlocked_tier 还是 "none"，后端会尝试兜底解锁
        // 如果第一次还是 none，可能是 Stripe metadata 有问题，重试一次
        if (data.paid && data.assessment_id) {
          if (!data.unlocked_tier || normalizeTier(data.unlocked_tier) === "none") {
            if (retryCount < 1) {
              // 只重试一次，因为后端有兜底逻辑，应该第一次就能成功
              console.log(`[支付验证] unlocked_tier 仍为 none，等待 1 秒后重试（后端会尝试兜底解锁）... (${retryCount + 1}/1)`);
              setTimeout(() => {
                verifyPayment(retryCount + 1);
              }, 1000);
              return;
            } else {
              console.warn("⚠️ 警告：支付成功但 unlocked_tier 仍为 none，后端兜底解锁可能失败");
            }
          }
          
          // ✅ 只要支付成功且有 assessment_id，就继续处理（即使 unlocked_tier 是 none）
          if (data.assessment_id) {
          // ✅ Step 1: 保存 assessment_id 和 unlocked_tier（使用正确的 key）
          const normalizedTier = normalizeTier(data.unlocked_tier);
          const assessmentId = data.assessment_id;
          
          console.log("✅ 支付成功，收到数据：", {
            assessment_id: assessmentId,
            unlocked_tier: data.unlocked_tier,
            normalized_tier: normalizedTier,
            paid: data.paid,
          });
          
          // 保存 assessment_id（关键：贯穿支付流程）
          sessionStorage.setItem("assessment_id", assessmentId);
          localStorage.setItem("assessment_id", assessmentId);
          
          // ✅ Step 2: 使用 assessment_id 作为 key 保存 unlocked_tier
          const tierKey = `assessment_unlocked_tier:${assessmentId}`;
          sessionStorage.setItem(tierKey, normalizedTier);
          localStorage.setItem(tierKey, normalizedTier);
          
          console.log("✅ 已保存解锁状态：", {
            tierKey,
            tier: normalizedTier,
          });
          
          // ✅ Step 3: 重新获取完整的评估结果（基于最新的 unlocked_tier）
          const storedInput = sessionStorage.getItem("assessment_input");
          if (storedInput) {
            try {
              const inputData = JSON.parse(storedInput);
              
              // 重新请求完整的 assessment（传递 assessment_id 参数，让后端使用最新的 unlocked_tier）
              const refreshResponse = await fetch(
                `${API_BASE_URL}/api/v1/compliance/assess?assessment_id=${encodeURIComponent(assessmentId)}`,
                {
                  method: "POST",
                  headers: {
                    "Content-Type": "application/json",
                  },
                  body: JSON.stringify(inputData),
                  cache: "no-store",
                }
              );

              if (refreshResponse.ok) {
                const resultData = await refreshResponse.json();
                
                // 确保使用正确的 assessment_id
                if (resultData.id) {
                  sessionStorage.setItem("assessment_id", resultData.id);
                  localStorage.setItem("assessment_id", resultData.id);
                }
                
                // ✅ 覆盖旧的 assessment_result，确保包含完整的付费内容
                sessionStorage.setItem("assessment_result", JSON.stringify(resultData));
                
                const reasonsCount = resultData.decision_summary?.reasons?.length || 0;
                const actionsCount = resultData.decision_summary?.recommended_actions?.length || 0;
                const ignoreCount = resultData.decision_summary?.risk_if_ignore?.length || 0;
                
                console.log("✅ 已刷新评估结果，付费内容：", {
                  unlockedTier: normalizedTier,
                  reasons: reasonsCount,
                  actions: actionsCount,
                  ignore: ignoreCount,
                  decision_level: resultData.decision_summary?.level,
                  paywall: resultData.decision_summary?.paywall,
                });
                
                // ⚠️ 如果解锁了但内容仍为空，显示警告
                if (normalizedTier !== "none" && reasonsCount === 0 && actionsCount === 0 && ignoreCount === 0) {
                  console.warn("⚠️ 警告：已解锁但付费内容为空！", {
                    tier: normalizedTier,
                    decision_level: resultData.decision_summary?.level,
                    paywall: resultData.decision_summary?.paywall,
                  });
                }
              } else {
                const errorText = await refreshResponse.text();
                console.error("❌ Failed to refresh assessment result:", refreshResponse.status, errorText);
              }
            } catch (error) {
              console.error("Failed to refresh assessment result:", error);
            }
          }

          setStatus("success");
          setMessage("支付成功 🎉\n正在为你解锁本次评估的完整决策内容…");

          // ✅ Step 4: 跳转回结果页，并带上 assessment_id
          setTimeout(() => {
            router.replace(`/assessment/result?assessment_id=${encodeURIComponent(assessmentId)}`);
          }, 1500);
          } else {
            // 支付成功但没有 unlocked_tier（可能是 webhook 延迟）
            console.warn("⚠️ 支付成功但 unlocked_tier 为空，跳转到 result 页让用户手动刷新");
            setStatus("success");
            setMessage("✅ 支付成功，正在跳转...");
            setTimeout(() => {
              router.replace(`/assessment/result?assessment_id=${encodeURIComponent(data.assessment_id)}`);
            }, 1500);
          }
        } else {
          setStatus("error");
          setMessage("支付验证失败，请重试");
          setTimeout(() => {
            router.replace("/assessment/result");
          }, 2000);
        }
      } catch (error) {
        console.error("Payment verification error:", error);
        setStatus("error");
        setMessage("支付处理失败，请重试");
        setTimeout(() => {
          router.replace("/assessment/result");
        }, 2000);
      }
    };

    verifyPayment();
  }, [searchParams, router]);

  return (
    <Layout>
      <div className="min-h-screen flex items-center justify-center px-4 py-20">
        <div className="max-w-md w-full bg-slate-800/50 rounded-xl p-8 border border-slate-700 text-center">
          {status === "loading" && (
            <>
              <div className="mb-4">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-purple-500 border-t-transparent"></div>
              </div>
              <p className="text-gray-100 text-lg">{message}</p>
            </>
          )}

          {status === "success" && (
            <>
              <div className="mb-4 text-4xl">🎉</div>
              <p className="text-gray-100 text-lg font-semibold whitespace-pre-line">{message}</p>
              <p className="text-gray-400 text-sm mt-2">正在跳转...</p>
              <p className="text-gray-500 text-xs mt-2">
                本平台不提供法律/税务建议；涉及历史问题请咨询专业人士。
                数字化服务一经交付不支持退款。
              </p>
            </>
          )}

          {status === "error" && (
            <>
              <div className="mb-4 text-4xl">❌</div>
              <p className="text-gray-100 text-lg font-semibold">{message}</p>
              <p className="text-gray-400 text-sm mt-2">正在跳转...</p>
            </>
          )}
        </div>
      </div>
    </Layout>
  );
}

