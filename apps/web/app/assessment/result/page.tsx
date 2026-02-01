"use client";

import React, { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Layout from "@/app/components/Layout";
import ExpertPartnersPlaceholder from "../components/ExpertPartnersPlaceholder";

/**
 * 约定：后端 compliance/assess 返回结构（你可以按这个冻结 v1）
 * {
 *   input: {...},
 *   risk_score: number,
 *   risk_level: "green"|"yellow"|"orange"|"red",
 *   findings: Finding[],
 *   meta: {...},
 *   decision_summary: {
 *     decision_code: string,
 *     title: string,
 *     conclusion: string,
 *     confidence_level: "high"|"medium"|"low",
 *     next_review_window: string,
 *     paywall: "none"|"basic_15"|"expert_39",
 *     pay_reason?: string,
 *     top_risks: Finding[],
 *     reasons: string[],
 *     recommended_actions: string[],
 *     risk_if_ignore: string[],
 *     expert_pack?: { ... }
 *   }
 * }
 */

type Severity = "info" | "low" | "medium" | "high";
type RiskLevel = "green" | "yellow" | "orange" | "red";
type PaywallTier = "none" | "basic_15" | "expert_39";

// 标准化 tier 字符串（处理各种可能的格式）
function normalizeTier(t?: string | null): PaywallTier {
  const x = (t ?? "").trim().toLowerCase().replaceAll("-", "_");
  if (!x || x === "none" || x === "free") return "none";
  if (["basic", "basic15", "basic_15"].includes(x)) return "basic_15";
  if (["expert", "expert39", "expert_39", "pro"].includes(x)) return "expert_39";
  if (x === "basic_15" || x === "expert_39") return x;
  return "none";
}

// ✅ 复评提示常量
const REEVALUATE_AFTER_DAYS = 30; // 30天后提示复评

// 计算评估是否过期（使用 calendar day diff，避免夏令时误差）
function isAssessmentExpired(createdAt: string | null | undefined): boolean {
  if (!createdAt) return false;
  try {
    const createdDate = new Date(createdAt);
    const now = new Date();
    
    // ✅ 使用 calendar day diff（避免夏令时误差）
    // 将两个日期都转换为 YYYY-MM-DD 格式的日期字符串，然后计算天数差
    const createdDateStr = createdDate.toISOString().split('T')[0];
    const nowDateStr = now.toISOString().split('T')[0];
    
    const createdDateOnly = new Date(createdDateStr + 'T00:00:00Z');
    const nowDateOnly = new Date(nowDateStr + 'T00:00:00Z');
    
    const daysPassed = Math.floor((nowDateOnly.getTime() - createdDateOnly.getTime()) / (1000 * 60 * 60 * 24));
    return daysPassed >= REEVALUATE_AFTER_DAYS;
  } catch (e) {
    console.warn("Failed to parse created_at:", e);
    return false;
  }
}

// 格式化评估日期（用于显示）
function formatAssessmentDate(dateString: string | null | undefined): string {
  if (!dateString) return "未知日期";
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString("zh-CN", { year: "numeric", month: "long", day: "numeric" });
  } catch (e) {
    return dateString;
  }
}

// ---------------- UX 文案/结构化工具（纯前端） ----------------

// 把 actions 粗分类：1小时 / 3天内 / 30天内
function bucketizeActions(actions: string[]) {
  const a1h: string[] = [];
  const a3d: string[] = [];
  const a30d: string[] = [];

  const pushUnique = (arr: string[], item: string) => {
    if (!arr.includes(item)) arr.push(item);
  };

  for (const a of actions || []) {
    const x = (a || "").toLowerCase();

    // ✅ 1小时：整理/下载/截图/对齐/建表/检查
    if (
      /整理|汇总|对齐|核对|下载|导出|截图|建立|建一个|做一个|检查|自查|清单|归档|分类/.test(a) ||
      /(download|export|screenshot|reconcile|check|organize|list)/.test(x)
    ) {
      pushUnique(a1h, a);
      continue;
    }

    // ✅ 3天内：联系 gestor/预约/补申报/补材料/提交
    if (
      /预约|联系|提交|补交|补申报|更正|登记|申报|开通|申请|咨询|gestor|会计|税务|登记备案/.test(a) ||
      /(book|submit|file|register|apply|accountant|gestor)/.test(x)
    ) {
      pushUnique(a3d, a);
      continue;
    }

    // ✅ 30天：流程化整改/制度/合同/社保/系统/长期
    if (
      /合同|社保|工资|用工|制度|流程|长期|每月|每季度|建立制度|系统|台账|发票闭环|pos/.test(a) ||
      /(contract|social security|payroll|process|monthly|quarterly|system|pos)/.test(x)
    ) {
      pushUnique(a30d, a);
      continue;
    }

    // 兜底：优先放 3天内（更像需要行动）
    pushUnique(a3d, a);
  }

  // 保底：如果某个桶为空，把后面的补进去一点
  const all = actions || [];
  if (a1h.length === 0 && all[0]) a1h.push(all[0]);
  if (a3d.length === 0 && all[1]) a3d.push(all[1]);
  if (a30d.length === 0 && all[2]) a30d.push(all[2]);

  return { a1h: a1h.slice(0, 4), a3d: a3d.slice(0, 5), a30d: a30d.slice(0, 6) };
}

// reasons → 3句人话（结合 topFinding + 用户输入（如果有））
function makeHumanReasons(params: {
  decisionTitle: string;
  topFindingTitle?: string;
  topFindingDetail?: string;
  input?: Record<string, any>;
  riskScore: number;
  riskLevel: string;
}) {
  const { decisionTitle, topFindingTitle, input, riskScore, riskLevel } = params;

  const income = input?.monthly_income;
  const emp = input?.employee_count;
  const stage = input?.stage;
  const industry = input?.industry;

  const s1 = `你现在的结论是「${decisionTitle}」，风险分数 ${riskScore}（${riskLevel}），说明目前的经营状态"容易被追溯/解释不足"。`;

  const s2 = topFindingTitle
    ? `最关键的触发点是「${topFindingTitle}」——这类问题通常会在 POS 流水/VAT 申报/消费者投诉/市政检查中被快速对上。`
    : `最关键的触发点通常来自"收入与票据/申报/用工记录对不上"，容易被 POS 数据比对、VAT 申报记录或消费者投诉触发检查。`;

  const s3Parts: string[] = [];
  if (income) s3Parts.push(`你填的月收入约 €${income}`);
  if (typeof emp === "number") s3Parts.push(`员工数 ${emp}`);
  if (industry) s3Parts.push(`行业：${industry}`);
  if (stage) s3Parts.push(`阶段：${stage}`);

  const s3 = `你现在要做的不是"解释"，而是把材料链条补齐（票据 → 记账 → 申报 → 用工/合同）。${
    s3Parts.length ? `（当前输入：${s3Parts.join("，")}）` : ""
  }`;

  return [s1, s2, s3];
}

// ignore → 税务局执法路径（叙事化）
function makeEnforcementPath(ignore: string[], topFindingTitle?: string) {
  // 用你的 ignoreTop3 做素材，但包装成路径
  const i = (ignore || []).slice(0, 3);

  const step1 = `1）线索进入：税务局常见线索来自 POS 数据比对、VAT/IRPF 申报记录、消费者投诉或市政检查（尤其是${topFindingTitle ? `围绕「${topFindingTitle}」` : "收入与票据"}）。`;

  const step2 = `2）触发动作：先发通知/要求补材料（发票、账本、合同、工资社保、收款凭证）。如果解释不闭环，会被要求补申报/更正。`;

  const step3 = `3）结果升级：常见结果是补税 + 罚款 + 滞纳金；并可能进入更频繁的后续抽查/复核。`;

  const bullets = i.length
    ? `你当前最可能遇到的后果点：\n- ${i.join("\n- ")}`
    : `你当前最可能遇到的后果点：\n- 补税/补申报\n- 罚款与滞纳金\n- 更频繁的复核抽查`;

  return { step1, step2, step3, bullets };
}

type Finding = {
  code: string;
  title: string;
  detail: string;
  severity: Severity;
  legal_ref?: string | null;
  pro_only?: boolean;
  explain_difficulty?: "low" | "medium" | "high";
  trigger_sources?: string[];
};

type RiskExplain = {
  label: string;
  one_liner: string;
  stage_note: string;
  main_drivers: string[];
  risk_stage?: "A" | "B" | "C" | "D";
};

type DecisionSummary = {
  level: string;
  decision_code?: string;  // 用于 debug
  decision_intent?: string;
  title: string;
  conclusion: string;
  confidence_level: "high" | "medium" | "low";
  confidence_reason?: string;  // ✅ 新增：置信度原因
  next_review_window: string;
  paywall: PaywallTier;
  pay_reason?: string | null;
  top_risks: Finding[];
  reasons: string[];
  recommended_actions: string[];
  risk_if_ignore: string[];
  risk_explain?: RiskExplain;  // ✅ 新增：风险分数解释（咨询师风格）
  dont_do?: string[];
  expert_pack?: {
    risk_groups?: Record<string, any[]>;
    roadmap_30d?: Array<{ week?: string; tasks?: string[] | string }>;
    documents_pack?: string[];
    self_audit_checklist?: string[];
    decision_guidance?: {
      need_professional?: string;
      suggested_roles?: string[];
      reason?: string;
    };
    cadence_90d?: string[];
    score_breakdown?: {
      industry_base?: { score: number; reason: string };
      signals?: Array<{ code: string; score: number; reason: string }>;
      income?: { score: number; band: string };
      employee?: { score: number; reason: string };
      pos?: { score: number; reason: string };
      deductions?: Array<any>;
    };
    enforcement_path?: Array<{
      step: number;
      title: string;
      description: string;
    }>;
  } | null;
};

type AssessmentResult = {
  input?: Record<string, any>;
  risk_score: number;
  risk_level: RiskLevel;
  findings: Finding[];
  meta?: Record<string, any>;
  decision_summary: DecisionSummary;
};

function badgeForRisk(level: RiskLevel) {
  const map: Record<RiskLevel, { label: string; cls: string }> = {
    green: { label: "🟢 低风险", cls: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30" },
    yellow: { label: "🟡 中风险", cls: "bg-yellow-500/15 text-yellow-200 border-yellow-500/30" },
    orange: { label: "🟠 高风险", cls: "bg-orange-500/15 text-orange-200 border-orange-500/30" },
    red: { label: "🔴 极高风险", cls: "bg-red-500/15 text-red-200 border-red-500/30" },
  };
  return map[level];
}

function badgeForRiskStage(stage?: RiskExplain["risk_stage"]) {
  if (!stage) return null;
  const map: Record<NonNullable<RiskExplain["risk_stage"]>, { label: string; cls: string }> = {
    A: { label: "阶段 A", cls: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30" },
    B: { label: "阶段 B", cls: "bg-yellow-500/15 text-yellow-200 border-yellow-500/30" },
    C: { label: "阶段 C", cls: "bg-orange-500/15 text-orange-200 border-orange-500/30" },
    D: { label: "阶段 D", cls: "bg-red-500/15 text-red-200 border-red-500/30" },
  };
  return map[stage];
}

function badgeForConfidence(c: DecisionSummary["confidence_level"]) {
  const map = {
    high: { label: "可信度：高", cls: "bg-slate-800/50 text-gray-100 border-slate-700" },
    medium: { label: "可信度：中", cls: "bg-slate-800/50 text-gray-200 border-slate-700" },
    low: { label: "可信度：低（信息不足）", cls: "bg-slate-800/50 text-gray-300 border-slate-700" },
  };
  return map[c];
}

function decisionGuidanceLabel(level?: string) {
  const map: Record<string, string> = {
    no: "无需",
    consider: "建议",
    strongly_consider: "强烈建议咨询（至少做一次材料链梳理）",
    yes: "需要",
  };
  return level ? map[level] || level : "—";
}

function explainDifficultyMeta(level?: Finding["explain_difficulty"]) {
  const map: Record<NonNullable<Finding["explain_difficulty"]>, { label: string; cls: string }> = {
    low: { label: "解释难度：低", cls: "bg-emerald-500/10 text-emerald-200 border-emerald-500/30" },
    medium: { label: "解释难度：中", cls: "bg-yellow-500/10 text-yellow-200 border-yellow-500/30" },
    high: { label: "解释难度：高", cls: "bg-red-500/10 text-red-200 border-red-500/30" },
  };
  return level ? map[level] : null;
}

function paywallCopy(tier: PaywallTier) {
  if (tier === "basic_15") {
    return {
      price: "€15",
      title: "自查版（Self-check）",
      subtitle: "你将看到：阶段+解释失败点摘要、基础行动清单、基础 PDF",
      cta: "解锁 €15",
    };
  }
  if (tier === "expert_39") {
    return {
      price: "€39",
      title: "决策版（Decision Pack）",
      subtitle: "你将看到：完整阶段解释、不该做的事、材料清单/自检表、专业协助提示",
      cta: "解锁 €39",
    };
  }
  return null;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export default function AssessmentResultPage() {
  const router = useRouter();

  const [data, setData] = useState<AssessmentResult | null>(null);
  const [unlockedTier, setUnlockedTier] = useState<PaywallTier>("none");
  const [showPaySheet, setShowPaySheet] = useState(false);
  const [paySheetTier, setPaySheetTier] = useState<PaywallTier>("basic_15"); // ✅ 新增：支持 €15/€39
  const [selectedTier, setSelectedTier] = useState<PaywallTier>("basic_15"); // ✅ A2: BottomSheet 选择的 tier
  const [assessmentCreatedAt, setAssessmentCreatedAt] = useState<string | null>(null); // ✅ 评估创建时间
  const [assessmentNotFound, setAssessmentNotFound] = useState(false); // ✅ assessment_id 不存在标记

  // 1) 载入 sessionStorage 的结果（无则回 start）
  useEffect(() => {
    const run = async () => {
      try {
        // ✅ Step 1: 获取 assessment_id（优先从 URL，其次从 sessionStorage，最后从 localStorage）
        const assessmentId =
          new URLSearchParams(window.location.search).get("assessment_id") ||
          sessionStorage.getItem("assessment_id") ||
          localStorage.getItem("assessment_id");
        
        if (!assessmentId) {
          console.warn("No assessment_id found, redirecting to start");
          router.replace("/assessment/start");
          return;
        }

        // 保存 assessment_id（确保后续使用）
        sessionStorage.setItem("assessment_id", assessmentId);
        localStorage.setItem("assessment_id", assessmentId);
        
        // ✅ Step 2: 先尝试从 sessionStorage 加载初始数据（快速显示）
        const raw = sessionStorage.getItem("assessment_result");
        if (raw) {
          try {
            const parsed = JSON.parse(raw) as AssessmentResult;
            setData(parsed);
          } catch (e) {
            console.warn("Failed to parse cached result:", e);
          }
        }
        
        // ✅ Step 3: 读取当前解锁状态（从存储）
        const tierKey = `assessment_unlocked_tier:${assessmentId}`;
        const savedTier = sessionStorage.getItem(tierKey) || localStorage.getItem(tierKey);
        setUnlockedTier(normalizeTier(savedTier));

        // ✅ Step 4: 用 assessment_id 拉最新 unlocked_tier（权威来源）
        try {
          // 1) 先拉权威 unlocked_tier（数据库）
          const r = await fetch(`${API_BASE_URL}/api/v1/compliance/assessments/${assessmentId}`, {
            cache: "no-store",
          });
          if (!r.ok) {
            if (r.status === 404) {
              // ✅ assessment_id 不存在，显示友好错误页
              setData(null);
              setAssessmentNotFound(true);
              return;
            }
            console.warn("Failed to fetch assessment:", r.statusText);
            return;
          }
          const a = await r.json();
          const tier = normalizeTier(a.unlocked_tier);

          setUnlockedTier(tier);
          
          // ✅ 保存评估创建时间（用于过期检查）
          if (a.created_at) {
            setAssessmentCreatedAt(a.created_at);
          }

          // 2) 存起来（避免刷新丢）
          const tierKey = `assessment_unlocked_tier:${assessmentId}`;
          sessionStorage.setItem(tierKey, tier);
          localStorage.setItem(tierKey, tier);

          // ✅ Step 5: 用最新 tier 重新 POST /assess，把付费字段拿回来
          // ⚠️ 关键：必须重新请求，让后端用最新的 unlocked_tier 重新生成 decision_summary
          const rawInput = sessionStorage.getItem("assessment_input");
          if (!rawInput) {
            console.warn("No assessment_input found in sessionStorage");
            return;
          }
          const input = JSON.parse(rawInput);

          console.log("🔄 重新请求 assess，使用最新的 unlocked_tier:", tier);
          console.log("📤 请求参数:", { assessment_id: assessmentId, ...input });

          // ✅ 关键：传递 assessment_id 作为 query 参数，让后端从数据库读取最新的 unlocked_tier
          const latest = await fetch(
            `${API_BASE_URL}/api/v1/compliance/assess?assessment_id=${encodeURIComponent(assessmentId)}`,
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(input),
              cache: "no-store",
            }
          );

          if (!latest.ok) {
            const errorText = await latest.text();
            console.error("❌ Failed to refresh assessment result:", latest.status, errorText);
            return;
          }
          const latestJson = await latest.json();
          
          // ✅ 验证付费内容是否正确返回
          const reasonsCount = latestJson.decision_summary?.reasons?.length || 0;
          const actionsCount = latestJson.decision_summary?.recommended_actions?.length || 0;
          const ignoreCount = latestJson.decision_summary?.risk_if_ignore?.length || 0;
          
          console.log("✅ 已刷新评估结果，付费内容：", {
            unlockedTier: tier,
            reasons: reasonsCount,
            actions: actionsCount,
            ignore: ignoreCount,
            decision_level: latestJson.decision_summary?.level,
            paywall: latestJson.decision_summary?.paywall,
          });
          
          // ⚠️ 如果解锁了但内容仍为空，显示警告
          if (tier !== "none" && reasonsCount === 0 && actionsCount === 0 && ignoreCount === 0) {
            console.warn("⚠️ 警告：已解锁但付费内容为空！", {
              tier,
              decision_level: latestJson.decision_summary?.level,
              paywall: latestJson.decision_summary?.paywall,
            });
          }
          
          // ✅ 更新数据（包含完整的付费内容）
          setData(latestJson);

          // 同步最新 result
          sessionStorage.setItem("assessment_result", JSON.stringify(latestJson));
          
          // 确保 assessment_id 保存
          if (latestJson.id) {
            sessionStorage.setItem("assessment_id", latestJson.id);
            localStorage.setItem("assessment_id", latestJson.id);
          }
        } catch (e) {
          console.error("Failed to refresh assessment:", e);
        }
      } catch (error) {
        console.error("Failed to load assessment result:", error);
        router.replace("/assessment/start");
      }
    };

    run();
  }, [router]);

  const decision = data?.decision_summary;
  const input = data?.input || undefined;

  // ✅ 新增：topFinding（用于生成人话）
  const topFinding = useMemo(() => {
    // 你已有 keyFinding 也行，这里按 finding 最高优先取
    const arr = data?.findings || [];
    if (!arr.length) return null;
    const sorted = [...arr].sort((a, b) => (b.severity === "high" ? 3 : b.severity === "medium" ? 2 : b.severity === "low" ? 1 : 0) -
                                       (a.severity === "high" ? 3 : a.severity === "medium" ? 2 : a.severity === "low" ? 1 : 0));
    return sorted[0];
  }, [data?.findings]);

  // ✅ 新增：humanReasons（3句人话）
  const humanReasons = useMemo(() => {
    if (!decision || !data) return [];
    return makeHumanReasons({
      decisionTitle: decision.title,
      topFindingTitle: topFinding?.title,
      topFindingDetail: topFinding?.detail,
      input,
      riskScore: data.risk_score,
      riskLevel: data.risk_level,
    });
  }, [decision?.title, topFinding?.title, topFinding?.detail, input, data?.risk_score, data?.risk_level]);

  // ✅ 新增：actionBuckets（1小时/3天/30天分类）
  const actionBuckets = useMemo(() => {
    if (!decision?.recommended_actions) return { a1h: [], a3d: [], a30d: [] };
    return bucketizeActions(decision.recommended_actions);
  }, [decision?.recommended_actions]);

  // ✅ 新增：enforcementPath（执法路径）
  const enforcementPath = useMemo(() => {
    if (!decision?.risk_if_ignore) return { step1: "", step2: "", step3: "", bullets: "" };
    return makeEnforcementPath(decision.risk_if_ignore, topFinding?.title);
  }, [decision?.risk_if_ignore, topFinding?.title]);

  // 2) 当前是否需要付费墙（由后端给 paywall）
  const requiredTier: PaywallTier = decision?.paywall ?? "none";

  // ✅ 新增：keyFinding 计算逻辑（优先 INC_HIGH / EMP_REQUIRED / POS_TRACKABLE / COMBO…）
  const keyFinding = useMemo(() => {
    if (!data?.findings || !decision?.top_risks) return null;
    
    // 优先级顺序：INC_HIGH > EMP_REQUIRED > POS_TRACKABLE > COMBO > 其他
    const priorityCodes = [
      "INC_HIGH",
      "EMP_REQUIRED", 
      "POS_TRACKABLE",
      "COMBO",
    ];
    
    // 先检查 top_risks
    for (const code of priorityCodes) {
      const found = decision.top_risks.find(f => f.code?.includes(code) || f.title?.includes("收入") || f.title?.includes("用工") || f.title?.includes("POS") || f.title?.includes("组合"));
      if (found) return found;
    }
    
    // 再检查所有 findings
    for (const code of priorityCodes) {
      const found = data.findings.find(f => f.code?.includes(code) || f.title?.includes("收入") || f.title?.includes("用工") || f.title?.includes("POS") || f.title?.includes("组合"));
      if (found) return found;
    }
    
    // 最后返回第一个 high severity 的
    const highSeverity = decision.top_risks.find(f => f.severity === "high") || data.findings.find(f => f.severity === "high");
    if (highSeverity) return highSeverity;
    
    // 兜底：返回第一个 top_risk
    return decision.top_risks[0] || null;
  }, [data?.findings, decision?.top_risks]);

  // 3) 当前是否已经解锁了足够层级
  const isUnlocked = useMemo(() => {
    if (!decision) return false;
    if (requiredTier === "none") return true;
    if (requiredTier === "basic_15") return unlockedTier === "basic_15" || unlockedTier === "expert_39";
    if (requiredTier === "expert_39") return unlockedTier === "expert_39";
    return false;
  }, [decision, requiredTier, unlockedTier]);

  // 4) 点击解锁（接 Stripe）
  async function handleUnlockConfirm(tier: PaywallTier = "basic_15") {
    setShowPaySheet(false);
    
    try {
      // 关键：assessment_id 只能来自 POST /assess 返回的 id，不能生成
      const assessmentId = sessionStorage.getItem("assessment_id");
      if (!assessmentId) {
        alert("缺少 assessment_id，请重新进行评估");
        router.push("/assessment/start");
        return;
      }
      
      // 获取或生成 user_id（简化版，使用 localStorage）
      let userId = localStorage.getItem("user_id");
      if (!userId) {
        userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        localStorage.setItem("user_id", userId);
      }
      
      // A. tier 统一：直接使用 tier（已经是 "basic_15" 或 "expert_39"）
      const response = await fetch(`${API_BASE_URL}/api/v1/stripe/create-checkout-session`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ 
          tier: tier,  // 直接传递 "basic_15" 或 "expert_39"
          assessment_id: assessmentId,
          user_id: userId,
        }),
      });

      if (!response.ok) {
        throw new Error("创建支付会话失败");
      }

      const data = await response.json();
      window.location.href = data.checkout_url;
    } catch (error) {
      console.error("Error:", error);
      alert("支付失败，请检查 Stripe 配置");
    }
  }

  // ✅ assessment_id 不存在时显示友好错误页
  if (assessmentNotFound) {
    return (
      <Layout>
        <div className="max-w-2xl mx-auto px-4 pt-20 pb-20">
          <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-8 text-center">
            <div className="text-4xl mb-4">📋</div>
            <div className="text-xl font-semibold text-gray-200 mb-3">
              没找到这次评估记录
            </div>
            <div className="text-gray-400 mb-6">
              你可以重新评估一次（约 3 分钟）。
            </div>
            <button
              onClick={() => router.push("/assessment/start")}
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-cyan-600 text-white font-semibold rounded-xl hover:from-purple-700 hover:to-cyan-700 transition-all"
            >
              <span>重新评估</span>
            </button>
          </div>
        </div>
      </Layout>
    );
  }

  if (!data || !decision) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-gray-400">加载中…</div>
        </div>
      </Layout>
    );
  }

  const riskBadge = badgeForRisk(data.risk_level);
  const stageBadge = badgeForRiskStage(decision.risk_explain?.risk_stage);
  const confBadge = badgeForConfidence(decision.confidence_level);
  const pay = paywallCopy(requiredTier);
  const assessmentId = typeof window !== "undefined" ? sessionStorage.getItem("assessment_id") : null;

  return (
    <Layout>
      <div className={`${unlockedTier === "basic_15" && isUnlocked ? "pb-24" : "pb-20"}`}>
        <div className="max-w-2xl mx-auto px-4 pt-8 pb-6">
      {/* Debug 信息（开发环境） */}
      {process.env.NODE_ENV === "development" && (
        <pre className="mb-4 bg-slate-800/50 rounded-xl border border-slate-700 p-3 text-xs text-gray-400 whitespace-pre-wrap">
          {`requiredTier: ${requiredTier}
unlockedTier(state): ${unlockedTier}
sessionStorage: ${typeof window !== "undefined" ? sessionStorage.getItem("assessment_unlocked_tier") : "n/a"}
localStorage: ${assessmentId ? localStorage.getItem(`assessment_unlocked_tier:${assessmentId}`) : "n/a"}
decision_code: ${decision.decision_code || decision.level || "n/a"}
assessment_id: ${assessmentId || "n/a"}
isUnlocked: ${isUnlocked}
paid_reasons_len: ${decision.reasons?.length ?? 0}
paid_actions_len: ${decision.recommended_actions?.length ?? 0}
paid_ignore_len: ${decision.risk_if_ignore?.length ?? 0}`}
        </pre>
      )}
      {/* 顶部摘要卡 */}
      <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700 mb-6">
        <div className="flex flex-wrap items-center gap-2">
          {stageBadge ? (
            <span className={`inline-flex items-center rounded-full border px-3 py-1 text-sm ${stageBadge.cls}`}>
              {stageBadge.label}
            </span>
          ) : (
            <span className={`inline-flex items-center rounded-full border px-3 py-1 text-sm ${riskBadge.cls}`}>
              {riskBadge.label}
            </span>
          )}
          {decision.risk_explain?.label && (
            <span className="text-xs text-gray-400">{decision.risk_explain.label}</span>
          )}
          <div className="relative inline-flex items-center">
            <span className={`inline-flex items-center rounded-full border px-3 py-1 text-sm ${confBadge.cls}`}>
              {confBadge.label}
            </span>
            {/* ✅ 可信度tooltip/说明 */}
            <div className="ml-2 group relative">
              <svg className="w-4 h-4 text-gray-400 cursor-help" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {/* Tooltip */}
              <div className="absolute left-0 bottom-full mb-2 w-64 p-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-gray-300 shadow-xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                可信度指的是当前判断基于的信息完整程度，而不是模型是否准确。当输入信息有限时，部分风险可能被低估或尚未显现。
              </div>
            </div>
          </div>
          {/* ✅ 移动端：在下方显示说明（小号灰字） */}
          <div className="w-full mt-2 text-xs text-gray-500 italic md:hidden">
            可信度指的是当前判断基于的信息完整程度，而不是模型是否准确。当输入信息有限时，部分风险可能被低估或尚未显现。
          </div>
        </div>

        <div className="mt-4">
          <div className="text-lg font-semibold">{decision.title}</div>
          <div className="mt-1 text-gray-300 leading-relaxed">{decision.conclusion}</div>
          {/* ✅ 新增：风险区间解释 */}
          {data.meta?.risk_band && (
            <div className="mt-3 text-sm text-gray-400 italic">
              这表示你已进入{data.meta.risk_band.label}：{data.meta.risk_band.explanation}
            </div>
          )}
          {/* ✅ 新增：置信度原因 */}
          {decision.confidence_reason && (
            <div className="mt-3 pt-3 border-t border-slate-700">
              <div className="text-xs text-white/60 mb-1">「为什么我们对这个判断有信心？」</div>
              <div className="text-sm text-gray-400 leading-relaxed">{decision.confidence_reason}</div>
              {/* ✅ 2️⃣ 更偏真人经验表达 */}
              <div className="mt-2 text-xs text-gray-500 italic">
                这些问题在实际检查中非常常见，也最容易通过补齐材料来解决。
              </div>
              {/* ✅ 3️⃣ 补充"人话解释"（增强信任） */}
              <div className="mt-2 text-xs text-gray-500">
                在实际检查中，类似情况下通常需要更多材料，才能确认是否存在被低估的风险点。
              </div>
            </div>
          )}
        </div>

        <div className="mt-4 flex items-end justify-between gap-4">
          <div>
            <div className="text-xs text-white/60">风险阶段</div>
            <div className="text-3xl font-semibold">{decision.risk_explain?.risk_stage ?? "-"}</div>
            {decision.risk_explain?.label && (
              <div className="mt-1 text-xs text-gray-400">{decision.risk_explain.label}</div>
            )}
            <div className="mt-2 text-xs text-gray-500 italic">
              分阶段用于表达“解释压力”强弱，并不等于违法或处罚结论。
            </div>
            <div className="mt-2 text-xs text-gray-500">
              参考分数：{data.risk_score}
            </div>
          </div>
          {decision.pay_reason ? (
            <div className="max-w-xs text-sm text-gray-400">
              <span className="text-white/90">为什么会建议解锁：</span>
              {decision.pay_reason}
            </div>
          ) : (
            <div className="text-sm text-white/60">—</div>
          )}
        </div>
      </div>

      {/* ✅ 新增："你的阶段意味着什么？" 咨询师风格解释区块 */}
      {decision.risk_explain && (
        <div className="mt-6 bg-slate-800/50 rounded-xl border border-slate-700 p-5">
          <div className="font-semibold mb-3">你的阶段意味着什么？</div>
          <div className="space-y-3">
            <div className="text-sm text-gray-200 leading-relaxed">
              {decision.risk_explain.one_liner}
            </div>
            {decision.risk_explain.stage_note && (
              <div className="text-xs text-gray-400 leading-relaxed italic">
                {decision.risk_explain.stage_note}
              </div>
            )}
            {decision.risk_explain.main_drivers && decision.risk_explain.main_drivers.length > 0 && (
              <div className="mt-3 pt-3 border-t border-slate-700">
                <div className="text-xs text-gray-400 mb-2">你的分数主要来自：</div>
                <div className="text-sm text-gray-300">
                  {decision.risk_explain.main_drivers.join(" + ")}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ✅ 更新："⚠️ 当前最需要关注的变化点" 卡片（使用 risk_explain.main_drivers） */}
      {decision.risk_explain?.main_drivers && decision.risk_explain.main_drivers.length > 0 && (
        <div className="mt-6 bg-gradient-to-br from-orange-500/10 to-red-500/10 rounded-xl border border-orange-500/30 p-5">
          <div className="flex items-start gap-3">
            <span className="text-2xl">⚠️</span>
            <div className="flex-1">
              <div className="font-semibold text-orange-200">当前最需要关注的变化点</div>
              <div className="mt-2 text-sm text-gray-200 leading-relaxed">
                如果你接下来 30 天内：{decision.risk_explain.main_drivers.map((d: string) => {
                  if (d.includes("收入")) return "收入继续增长";
                  if (d.includes("POS")) return "开始用 POS";
                  if (d.includes("用工") || d.includes("员工")) return "有帮工";
                  return d;
                }).join(" / ")} → 风险会明显上升。
              </div>
              {/* ✅ 3️⃣ 在「当前最需要关注的变化点」下加入动态 if 提示 */}
              <div className="mt-3 text-xs text-gray-400 italic">
                如果接下来 30 天内收入继续上升或新增员工，这一风险会明显放大。
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ✅ 复评提示卡片（超过30天时显示） */}
      {assessmentCreatedAt && isAssessmentExpired(assessmentCreatedAt) && (
        <div className="mt-6 bg-blue-900/20 border border-blue-800/50 rounded-xl p-5">
          <div className="flex items-start gap-3">
            <span className="text-xl">ℹ️</span>
            <div className="flex-1">
              <div className="text-sm font-semibold text-blue-200 mb-2">
                建议重新评估以获取最新判断
              </div>
              <div className="text-sm text-gray-300 leading-relaxed mb-3">
                本评估基于 {formatAssessmentDate(assessmentCreatedAt)} 的经营信息生成。
                <br />
                如果收入、员工数量、收款方式或经营模式已发生变化，建议进行一次新的复评，以获得最新判断。
              </div>
              {/* ✅ 触发条件清单 */}
              <div className="mt-3 pt-3 border-t border-blue-800/30">
                <div className="text-xs text-blue-300/80 font-medium mb-2">建议在以下情况发生时立即复评：</div>
                <ul className="text-xs text-gray-400 space-y-1 list-disc list-inside">
                  <li>收入连续上升</li>
                  <li>新增员工或外包</li>
                  <li>新增 POS 或平台收款</li>
                  <li>经营模式变化</li>
                </ul>
              </div>
              <button
                onClick={() => {
                  // ✅ 清理旧的评估相关缓存，确保新评估流程
                  const assessmentId = sessionStorage.getItem("assessment_id") || localStorage.getItem("assessment_id");
                  if (assessmentId) {
                    sessionStorage.removeItem("assessment_id");
                    localStorage.removeItem("assessment_id");
                    sessionStorage.removeItem("assessment_result");
                    sessionStorage.removeItem("assessment_input");
                    sessionStorage.removeItem(`assessment_unlocked_tier:${assessmentId}`);
                    localStorage.removeItem(`assessment_unlocked_tier:${assessmentId}`);
                  }
                  
                  // ✅ 获取上次选择的 stage（如果可用）
                  const lastStage = data?.input?.stage || null;
                  const startUrl = lastStage ? `/assessment/start?prefill_stage=${lastStage}` : "/assessment/start";
                  router.push(startUrl);
                }}
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600/20 border border-blue-500/50 text-blue-200 rounded-lg hover:bg-blue-600/30 transition-all text-sm font-medium"
              >
                <span>🔁</span>
                <span>重新评估（约 3 分钟）</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Top 3 解释失败点：改成优先级展示（🔥最优先 / 其次 / 背景） */}
      <div className="mt-6 bg-slate-800/50 rounded-xl border border-slate-700 p-5">
        <div className="font-semibold">你现在最容易解释失败的 3 个点</div>
        <div className="mt-3 space-y-3">
          {decision.top_risks?.map((f, idx) => {
            const priorityLabel = idx === 0 ? "🔥 最优先" : idx === 1 ? "其次" : "背景";
            const priorityClass = idx === 0 
              ? "border-orange-500/30 bg-orange-500/10" 
              : idx === 1 
              ? "border-yellow-500/20 bg-yellow-500/5" 
              : "border-white/10 bg-black/20";
            const diff = explainDifficultyMeta(f.explain_difficulty);
            
            return (
              <div key={`${f.code}-${idx}`} className={`rounded-xl border p-4 ${priorityClass}`}>
                <div className="flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-medium text-gray-400">{priorityLabel}</span>
                    <div className="font-medium">{f.title}</div>
                  </div>
                  <div className="text-xs text-white/60">{f.severity.toUpperCase()}</div>
                </div>
                <div className="mt-1 text-sm text-gray-300 leading-relaxed">{f.detail}</div>
                {/* ✅ 解释难度 + 触发来源 */}
                <div className="mt-2 flex flex-wrap items-center gap-2">
                  {diff && (
                    <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs ${diff.cls}`}>
                      {diff.label}
                    </span>
                  )}
                  {f.trigger_sources && f.trigger_sources.length > 0 && (
                    <span className="text-xs text-gray-400">
                      常见触发来源（用于理解风险）：{f.trigger_sources.slice(0, 3).join(" / ")}
                    </span>
                  )}
                </div>
                {/* ✅ 每条增加"为什么重要"解释 */}
                <div className="mt-2 text-xs text-gray-400 italic">
                  {f.severity === "high" && "重要：此问题最容易被税务或劳工部门关注，建议优先处理"}
                  {f.severity === "medium" && "注意：此问题可能引发后续核查，建议尽快处理"}
                  {f.severity === "low" && "提示：此问题需要关注，但优先级相对较低"}
                </div>
                {/* ✅ 第一条下面加"触发检查"提示 */}
                {idx === 0 && (
                  <div className="mt-2 rounded-lg bg-red-500/10 border border-red-500/20 px-3 py-2">
                    <div className="text-xs font-medium text-red-200">⚠️ 可能触发检查</div>
                    <div className="mt-1 text-xs text-red-100/80">此问题最容易被税务或劳工部门关注，建议优先处理</div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
        <div className="mt-3 text-xs text-gray-500">
          免责声明：本结果为风险提示与材料准备建议，不构成法律/税务意见。
        </div>
      </div>

      {/* ✅ 不该做什么（合规护身符） */}
      {decision.dont_do && decision.dont_do.length > 0 && (
        <div className="mt-6 bg-slate-900/40 rounded-xl border border-slate-700 p-5">
          <div className="font-semibold">你现在最不该做的事</div>
          <div className="mt-2 text-xs text-gray-400">
            这部分只提示“不要做什么”，不提供任何规避或操作细节。
          </div>
          <ul className="mt-3 space-y-2 text-sm text-gray-300">
            {decision.dont_do.slice(0, 4).map((item, idx) => (
              <li key={idx} className="rounded-xl border border-white/10 bg-black/20 p-3">
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* 风险识别概览（全部风险发现）- 免费展示，仅展示风险点本身 */}
      <div className="mt-6 bg-slate-800/50 rounded-xl border border-slate-700 p-5">
        <div className="flex items-center justify-between">
          <div className="font-semibold">风险识别概览（可展开查看）</div>
          <button
            onClick={() => router.push("/assessment/form")}
            className="text-sm text-gray-400 underline underline-offset-4"
          >
            进行复评
          </button>
        </div>

        <div className="mt-3 space-y-3">
          {data.findings.map((f, idx) => {
            const hiddenProOnly = !!f.pro_only && unlockedTier === "none" && requiredTier !== "none";
            return (
              <details key={`${f.code}-${idx}`} className="rounded-xl border border-white/10 bg-black/20 p-4">
                <summary className="cursor-pointer list-none">
                  <div className="flex items-center justify-between gap-3">
                    <div className="font-medium">{f.title}</div>
                    <div className="text-xs text-white/60">
                      {hiddenProOnly ? "PRO" : f.severity.toUpperCase()}
                    </div>
                  </div>
                  {f.legal_ref ? (
                    <div className="mt-1 text-xs text-white/45">{f.legal_ref}</div>
                  ) : null}
                </summary>

                <div className="mt-2 text-sm text-gray-300 leading-relaxed">
                  {hiddenProOnly ? (
                    <div className="rounded-lg border border-white/10 bg-white/5 p-3 text-gray-300">
                      此条为专业细节（解锁后可见）
                    </div>
                  ) : (
                    f.detail
                  )}
                </div>
              </details>
            );
          })}
        </div>
      </div>

      {/* ✅ 支付问题自救入口（已支付但未解锁时显示，在解锁卡之前） */}
      {requiredTier !== "none" && !isUnlocked && (
        <div className="mt-6 bg-yellow-900/20 border border-yellow-800/50 rounded-xl p-5">
          <div className="flex items-start gap-3">
            <span className="text-xl">⚠️</span>
            <div className="flex-1">
              <div className="text-sm font-semibold text-yellow-200 mb-2">
                已支付但未解锁？
              </div>
              <div className="text-sm text-gray-300 leading-relaxed mb-3">
                如果已完成支付但内容仍未解锁，请点击下方按钮刷新权限。
              </div>
              <button
                onClick={async () => {
                  try {
                    // ✅ 获取 session_id（从 URL 或 localStorage）
                    const sessionId = 
                      new URLSearchParams(window.location.search).get("session_id") ||
                      sessionStorage.getItem("stripe_session_id");
                    
                    if (!sessionId) {
                      alert("未找到支付会话 ID，请重新访问支付成功页面");
                      return;
                    }
                    
                    // ✅ 调用 /payment/status 刷新权限
                    const statusRes = await fetch(
                      `${API_BASE_URL}/api/v1/payment/status?session_id=${encodeURIComponent(sessionId)}`,
                      { cache: "no-store" }
                    );
                    
                    if (!statusRes.ok) {
                      alert("刷新权限失败，请稍后重试");
                      return;
                    }
                    
                    const statusData = await statusRes.json();
                    
                    if (statusData.paid && statusData.unlocked_tier) {
                      // ✅ 更新本地状态
                      const newTier = normalizeTier(statusData.unlocked_tier);
                      setUnlockedTier(newTier);
                      
                      // ✅ 保存到存储
                      const assessmentId = sessionStorage.getItem("assessment_id") || localStorage.getItem("assessment_id");
                      if (assessmentId) {
                        const tierKey = `assessment_unlocked_tier:${assessmentId}`;
                        sessionStorage.setItem(tierKey, newTier);
                        localStorage.setItem(tierKey, newTier);
                      }
                      
                      // ✅ 重新加载评估结果
                      window.location.reload();
                    } else {
                      alert("支付状态异常，请联系客服");
                    }
                  } catch (error) {
                    console.error("刷新权限失败:", error);
                    alert("刷新权限失败，请稍后重试");
                  }
                }}
                className="inline-flex items-center gap-2 px-4 py-2 bg-yellow-600/20 border border-yellow-500/50 text-yellow-200 rounded-lg hover:bg-yellow-600/30 transition-all text-sm font-medium"
              >
                <span>🔄</span>
                <span>点击这里刷新权限</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 🔓 解锁卡（整个页面最重要的卡）- 仅当 requiredTier != none 且未解锁 */}
      {requiredTier !== "none" && !isUnlocked && (
        <div className="mt-6 rounded-2xl border-2 border-purple-500/30 bg-gradient-to-br from-purple-500/10 to-cyan-500/10 p-6">
          <div className="text-center mb-5">
            <div className="text-xl font-bold text-gray-100 mb-2">
              想知道你现在该怎么做，才是最安全的吗？
            </div>
          </div>

          {/* ✅ 升级CTA前的引导文案 */}
          <div className="text-center text-xs text-gray-500 mb-3">
            解锁后可补充判断依据，用于确认是否存在当前未显现的风险点。
          </div>

          {/* 主 CTA：€15 */}
          <button
            onClick={() => {
              setPaySheetTier("basic_15");
              setShowPaySheet(true);
            }}
            className="w-full bg-gradient-to-r from-purple-600 to-cyan-600 text-white font-semibold py-4 rounded-xl hover:from-purple-700 hover:to-cyan-700 transition-all text-lg shadow-lg hover:shadow-xl mb-3"
          >
            🔓 解锁自查版 €15
          </button>
          <div className="text-center text-sm text-gray-400 mb-5">
            阶段摘要 + 解释失败点 + 基础行动清单 + 基础 PDF
          </div>

          {/* 分割线 */}
          <div className="flex items-center gap-3 mb-5">
            <div className="flex-1 h-px bg-gradient-to-r from-transparent via-slate-600 to-transparent"></div>
            <span className="text-xs text-gray-500">或</span>
            <div className="flex-1 h-px bg-gradient-to-r from-transparent via-slate-600 to-transparent"></div>
          </div>

          {/* 次 CTA：€39（弱化显示） */}
          <button
            onClick={() => {
              setPaySheetTier("expert_39");
              setShowPaySheet(true);
            }}
            className="w-full border-2 border-cyan-500/50 text-cyan-300 font-semibold py-3 rounded-xl hover:border-cyan-400 hover:bg-cyan-500/10 transition-all text-sm"
          >
            🎓 直接升级决策版 €39（一步到位）
          </button>
          <div className="text-center text-xs text-gray-500 mt-2">
            一次看清完整合规路径
          </div>
          {/* ✅ 决策版CTA前的引导文案 */}
          <div className="text-center text-xs text-gray-500 mt-2">
            解锁后可补充判断依据，用于确认是否存在当前未显现的风险点。
          </div>
          <div className="text-center text-xs text-gray-500 mt-2">
            本平台不提供法律/税务建议；涉及历史问题请咨询专业人士。
          </div>
        </div>
      )}

      {/* 付费内容（解锁后展示） */}
      <div id="paid-section" className="mt-6 space-y-4">
        {(requiredTier === "none" || isUnlocked) && (
          <>
            {/* 如果已解锁但付费内容为空，显示提示 */}
            {isUnlocked && 
             (!decision.reasons?.length && !decision.recommended_actions?.length && !decision.risk_if_ignore?.length) && (
              <div className="rounded-2xl border border-yellow-500/30 bg-yellow-500/10 p-5">
                <div className="font-semibold text-yellow-200">⚠️ 已解锁，但本次评估没有生成行动清单</div>
                  <div className="mt-2 text-sm text-yellow-100/80">
                  请进行复评或刷新页面获取最新结果
                </div>
                <button
                  onClick={() => router.push("/assessment/form")}
                  className="mt-3 bg-gradient-to-r from-purple-600 to-cyan-600 text-white font-semibold px-4 py-2 rounded-xl hover:from-purple-700 hover:to-cyan-700 transition-all text-sm"
                >
                  进行复评
                </button>
              </div>
            )}
            {/* ✅ A1: 升级到决策版 €39 卡片（只有 basic_15 已解锁时出现） */}
            {unlockedTier === "basic_15" && (
              <div className="mt-6 rounded-2xl border border-cyan-500/20 bg-cyan-500/5 p-5">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="font-semibold text-cyan-200">升级到决策版（€39）</div>
                    <div className="mt-1 text-sm text-gray-300">
                      解锁：完整阶段解释、不该做的事、材料清单/自检表、专业协助提示
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-semibold">€39</div>
                    <button
                      onClick={() => handleUnlockConfirm("expert_39")}
                      className="mt-2 rounded-xl bg-gradient-to-r from-purple-600 to-cyan-600 px-4 py-2 text-sm font-semibold text-white hover:from-purple-700 hover:to-cyan-700 transition-all"
                    >
                      立即升级
                    </button>
                  </div>
                </div>
                <div className="mt-3 text-xs text-gray-500">
                  本平台不提供法律/税务建议；涉及历史问题请咨询专业人士。
                </div>
              </div>
            )}

            {/* ✅ reasons → 3句人话 */}
            {humanReasons.length > 0 && (
              <div className="bg-slate-800/50 rounded-2xl border border-slate-700 p-5">
                <div className="font-semibold">为什么会得到这个结果</div>
                <div className="mt-2 space-y-2 text-sm text-gray-300 leading-relaxed">
                  {humanReasons.map((s, idx) => (
                    <div key={idx} className="rounded-xl border border-white/10 bg-black/20 p-3">
                      {s}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* ✅ actions → 1小时/3天/30天三段 */}
            {(actionBuckets.a1h.length > 0 || actionBuckets.a3d.length > 0 || actionBuckets.a30d.length > 0) && (
              <div className="bg-slate-800/50 rounded-2xl border border-slate-700 p-5">
                <div className="font-semibold">行动计划（按时间做，不会乱）</div>
                <div className="mt-2 text-xs text-white/55">建议：先做 1 小时清单 → 再做 3 天内 → 最后做 30 天整改。</div>

                {/* 1小时 */}
                {actionBuckets.a1h.length > 0 && (
                  <div className="mt-4 rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-4">
                    <div className="flex items-center justify-between">
                      <div className="font-semibold text-emerald-200">✅ 1 小时内能做完（立刻降低暴露）</div>
                      <div className="text-xs text-emerald-200/80">先做这个</div>
                    </div>
                    {/* ✅ 4️⃣ 行动清单前说明"为什么先做这些" */}
                    <div className="mt-2 text-xs text-gray-400 italic">
                      这些动作的目标是：让你在被问到时，5 分钟内就能拿出解释材料。
                    </div>
                    <div className="mt-3 space-y-2">
                      {actionBuckets.a1h.map((a, idx) => (
                        <label key={idx} className="flex gap-3 rounded-xl border border-white/10 bg-black/20 p-3 text-sm text-gray-200">
                          <input type="checkbox" className="mt-0.5" />
                          <span className="leading-relaxed">{a}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                )}

                {/* 3天内 */}
                {actionBuckets.a3d.length > 0 && (
                  <div className="mt-3 rounded-2xl border border-yellow-500/20 bg-yellow-500/5 p-4">
                    <div className="flex items-center justify-between">
                      <div className="font-semibold text-yellow-200">🟡 3 天内完成（补齐关键材料/申报）</div>
                      <div className="text-xs text-yellow-200/80">避免拖</div>
                    </div>
                    <div className="mt-3 space-y-2">
                      {actionBuckets.a3d.map((a, idx) => (
                        <label key={idx} className="flex gap-3 rounded-xl border border-white/10 bg-black/20 p-3 text-sm text-gray-200">
                          <input type="checkbox" className="mt-0.5" />
                          <span className="leading-relaxed">{a}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                )}

                {/* 30天内 */}
                {actionBuckets.a30d.length > 0 && (
                  <div className="mt-3 rounded-2xl border border-cyan-500/20 bg-cyan-500/5 p-4">
                    <div className="flex items-center justify-between">
                      <div className="font-semibold text-cyan-200">🔵 30 天内整改（把风险变成可控）</div>
                      <div className="text-xs text-cyan-200/80">长期稳定</div>
                    </div>
                    <div className="mt-3 space-y-2">
                      {actionBuckets.a30d.map((a, idx) => (
                        <label key={idx} className="flex gap-3 rounded-xl border border-white/10 bg-black/20 p-3 text-sm text-gray-200">
                          <input type="checkbox" className="mt-0.5" />
                          <span className="leading-relaxed">{a}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                )}
                {/* ✅ 行动清单结尾固定句（规范要求） */}
                <div className="mt-4 pt-4 border-t border-slate-700">
                  <div className="text-sm text-gray-300 italic">
                    完成上述步骤后，建议进行一次复评，确认风险是否已明显下降。
                  </div>
                </div>
              </div>
            )}

            {/* ✅ ignore → 执法路径（让用户更"有画面"） */}
            {enforcementPath.step1 && (
              <div className="bg-slate-800/50 rounded-2xl border border-slate-700 p-5">
                <div className="font-semibold">税务局通常会怎么做（执法路径）</div>
                <div className="mt-2 text-sm text-gray-400">
                  这是常见流程，让您知道为什么"材料闭环"最重要。
                </div>

                <div className="mt-4 space-y-3 text-sm text-gray-300 leading-relaxed">
                  <div className="rounded-xl border border-white/10 bg-black/20 p-3">{enforcementPath.step1}</div>
                  <div className="rounded-xl border border-white/10 bg-black/20 p-3">{enforcementPath.step2}</div>
                  <div className="rounded-xl border border-white/10 bg-black/20 p-3">{enforcementPath.step3}</div>
                </div>

                <div className="mt-4 rounded-xl border border-red-500/20 bg-red-500/5 p-4">
                  <div className="font-semibold text-red-200">您当前最可能遇到的后果点</div>
                  <pre className="mt-2 whitespace-pre-wrap text-sm text-gray-300">{enforcementPath.bullets}</pre>
                </div>
              </div>
            )}

            {/* ✅ A1: 升级到决策版 €39 卡片（只有 basic_15 已解锁时出现） */}
            {unlockedTier === "basic_15" && (
              <div className="mt-6 rounded-2xl border border-cyan-500/20 bg-cyan-500/5 p-5">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="font-semibold text-cyan-200">升级到决策版（€39）</div>
                    <div className="mt-1 text-sm text-gray-300">
                      解锁：完整阶段解释、不该做的事、材料清单/自检表、专业协助提示
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-semibold">€39</div>
                    <button
                      onClick={() => handleUnlockConfirm("expert_39")}
                      className="mt-2 rounded-xl bg-gradient-to-r from-purple-600 to-cyan-600 px-4 py-2 text-sm font-semibold text-white hover:from-purple-700 hover:to-cyan-700 transition-all"
                    >
                      立即升级
                    </button>
                  </div>
                </div>
                <div className="mt-3 text-xs text-gray-500">
                  本平台不提供法律/税务建议；涉及历史问题请咨询专业人士。
                </div>
              </div>
            )}

            {/* ✅ 已解锁决策版提示 */}
            {unlockedTier === "expert_39" && (
              <div className="bg-gradient-to-br from-purple-500/10 to-cyan-500/10 rounded-xl border border-purple-500/30 p-5">
                <div className="font-semibold text-purple-200">✅ 已解锁决策版</div>
                <div className="mt-2 text-sm text-gray-300">
                  您已拥有完整的决策版内容，包括阶段解释、材料清单与 30 天节奏
                </div>
              </div>
            )}

            {/* ✅ 下载 PDF 按钮（basic_15 或 expert_39 解锁时显示） */}
            {(unlockedTier === "basic_15" || unlockedTier === "expert_39") && data && (
              <div className="mt-6 bg-slate-800/50 rounded-xl border border-slate-700 p-5">
                <button
                  onClick={() => {
                    const assessmentId = 
                      new URLSearchParams(window.location.search).get("assessment_id") ||
                      sessionStorage.getItem("assessment_id") ||
                      localStorage.getItem("assessment_id");
                    
                    if (!assessmentId) {
                      alert("无法获取评估 ID");
                      return;
                    }
                    
                    // ✅ 简化：直接从数据库读取，不需要传递参数
                    const user_id = localStorage.getItem("user_id") || "";
                    const params = user_id ? `?user_id=${encodeURIComponent(user_id)}` : "";
                    const downloadUrl = `${API_BASE_URL}/api/v1/assessments/${assessmentId}/report.pdf${params}`;
                    window.location.href = downloadUrl;
                  }}
                  className="w-full bg-gradient-to-r from-purple-600 to-cyan-600 text-white font-semibold py-3 rounded-xl hover:from-purple-700 hover:to-cyan-700 transition-all text-sm flex items-center justify-center gap-2"
                >
                  <span>📄</span>
                  <span>下载完整合规报告（可交给 gestor / 顾问）</span>
                </button>
                <div className="mt-2 text-xs text-gray-500 text-center">
                  PDF 报告包含完整的评估结果和行动建议
                </div>
              </div>
            )}

            {/* ✅ 合作顾问占位板块（仅 expert_39 显示） */}
            {unlockedTier === "expert_39" && (
              <ExpertPartnersPlaceholder />
            )}

            {/* €39 决策版内容（只有 expert_39 解锁才展示） */}
            {unlockedTier === "expert_39" && decision.expert_pack && (
              <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-5">
                <div className="flex items-center justify-between mb-4">
                  <div className="font-semibold">🎓 决策版包含：</div>
                  <span className="text-xs text-white/60">Decision Pack</span>
                </div>

                {/* ✅ 新增：分数构成解析 */}
                {decision.expert_pack.score_breakdown && (
                  <div className="mb-4 pb-4 border-b border-slate-700">
                    <div className="text-sm font-semibold text-gray-200 mb-2">① 为什么你现在危险（分数构成）</div>
                    <div className="mt-2 space-y-2 text-sm text-gray-300">
                      {decision.expert_pack.score_breakdown.industry_base && (
                        <div className="flex justify-between">
                          <span>行业基础分：</span>
                          <span className="font-semibold">{decision.expert_pack.score_breakdown.industry_base.score} 分</span>
                        </div>
                      )}
                      {decision.expert_pack.score_breakdown.income && (
                        <div className="flex justify-between">
                          <span>收入分（{decision.expert_pack.score_breakdown.income.band}）：</span>
                          <span className="font-semibold">{decision.expert_pack.score_breakdown.income.score} 分</span>
                        </div>
                      )}
                      {decision.expert_pack.score_breakdown.employee && (
                        <div className="flex justify-between">
                          <span>员工分（{decision.expert_pack.score_breakdown.employee.reason}）：</span>
                          <span className="font-semibold">{decision.expert_pack.score_breakdown.employee.score} 分</span>
                        </div>
                      )}
                      {decision.expert_pack.score_breakdown.pos && (
                        <div className="flex justify-between">
                          <span>POS 分（{decision.expert_pack.score_breakdown.pos.reason}）：</span>
                          <span className="font-semibold">{decision.expert_pack.score_breakdown.pos.score} 分</span>
                        </div>
                      )}
                      {decision.expert_pack.score_breakdown.signals && decision.expert_pack.score_breakdown.signals.length > 0 && (
                        <div className="mt-2">
                          <div className="text-xs text-gray-400 mb-1">信号触发：</div>
                          {decision.expert_pack.score_breakdown.signals.slice(0, 3).map((s: any, idx: number) => (
                            <div key={idx} className="text-xs text-gray-400">
                              • {s.reason}: +{s.score} 分
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* ✅ 新增：执法路径 */}
                {decision.expert_pack.enforcement_path && Array.isArray(decision.expert_pack.enforcement_path) && decision.expert_pack.enforcement_path.length > 0 && (
                  <div className="mb-4 pb-4 border-b border-slate-700">
                    <div className="text-sm font-semibold text-gray-200 mb-2">② 税务局通常怎么走（执法路径）</div>
                    <div className="mt-2 space-y-3">
                      {decision.expert_pack.enforcement_path.map((step: any, idx: number) => (
                        <div key={idx} className="flex gap-3">
                          <div className="flex-shrink-0 w-6 h-6 rounded-full bg-purple-500/20 border border-purple-500/50 flex items-center justify-center text-xs font-semibold text-purple-300">
                            {step.step}
                          </div>
                          <div className="flex-1">
                            <div className="text-sm font-medium text-gray-200">{step.title}</div>
                            <div className="mt-1 text-xs text-gray-400 leading-relaxed">{step.description}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* ✅ 新增：是否需要专业人士 */}
                {decision.expert_pack.decision_guidance && (
                  <div className="mb-4 pb-4 border-b border-slate-700">
                    <div className="text-sm font-semibold text-gray-200 mb-2">③ 是否需要专业人士</div>
                    <div className="text-sm text-gray-300 leading-relaxed">
                      建议程度：{decisionGuidanceLabel(decision.expert_pack.decision_guidance.need_professional)}
                    </div>
                    {decision.expert_pack.decision_guidance.suggested_roles && decision.expert_pack.decision_guidance.suggested_roles.length > 0 && (
                      <div className="mt-1 text-xs text-gray-400">
                        建议角色：{decision.expert_pack.decision_guidance.suggested_roles.join(" / ")}
                      </div>
                    )}
                    {decision.expert_pack.decision_guidance.reason && (
                      <div className="mt-1 text-xs text-gray-400">{decision.expert_pack.decision_guidance.reason}</div>
                    )}
                    <div className="mt-2 text-xs text-gray-500">
                      本平台不提供法律/税务建议；涉及历史问题请咨询专业人士。
                    </div>
                  </div>
                )}

                {/* ✅ 新增：30/90 天节奏 */}
                {decision.expert_pack.cadence_90d && Array.isArray(decision.expert_pack.cadence_90d) && decision.expert_pack.cadence_90d.length > 0 && (
                  <div className="mb-4 pb-4 border-b border-slate-700">
                    <div className="text-sm font-semibold text-gray-200 mb-2">④ 30/90 天节奏</div>
                    <ul className="mt-2 list-disc pl-5 space-y-2 text-sm text-gray-300">
                      {decision.expert_pack.cadence_90d.map((s: string, idx: number) => (
                        <li key={idx}>{s}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {decision.expert_pack.risk_groups && Object.keys(decision.expert_pack.risk_groups).length > 0 ? (
                  <div className="mb-4 pb-4 border-b border-slate-700">
                    <div className="text-sm font-semibold text-gray-200 mb-2">风险分组</div>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {Object.keys(decision.expert_pack.risk_groups).map((t, idx) => {
                        const riskGroupMap: Record<string, { label: string; explanation: string }> = {
                          tax: { label: "税务风险", explanation: "常见于 VAT/开票" },
                          municipal: { label: "市政风险", explanation: "常见于市政检查/许可" },
                          consumer: { label: "消费者保护", explanation: "常见于消费者投诉" },
                          labor: { label: "用工风险", explanation: "常见于用工记录/社保" },
                          data: { label: "数据保护", explanation: "常见于数据保护/隐私" },
                          environment: { label: "环保风险", explanation: "常见于环保检查" },
                        };
                        const group = riskGroupMap[t] || { label: t, explanation: "" };
                        return (
                          <div key={idx} className="flex flex-col gap-1">
                            <span className="rounded-full border border-white/10 bg-black/20 px-3 py-1 text-xs text-gray-300">
                              {group.label}
                            </span>
                            {group.explanation && (
                              <span className="text-xs text-gray-500 italic text-center">
                                {group.explanation}
                              </span>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ) : null}

                {decision.expert_pack.roadmap_30d && Array.isArray(decision.expert_pack.roadmap_30d) && decision.expert_pack.roadmap_30d.length > 0 ? (
                  <div className="mb-4 pb-4 border-b border-slate-700">
                    <div className="text-sm font-semibold text-gray-200 mb-2">③ 接下来 30 天怎么做（路线图）</div>
                    <ol className="mt-2 list-decimal pl-5 space-y-2 text-sm text-gray-300">
                      {decision.expert_pack.roadmap_30d.map((item: any, idx: number) => (
                        <li key={idx}>
                          {item.week ? `${item.week}: ` : ""}
                          {Array.isArray(item.tasks) ? item.tasks.join(", ") : item}
                        </li>
                      ))}
                    </ol>
                  </div>
                ) : null}

                {decision.expert_pack.documents_pack && Array.isArray(decision.expert_pack.documents_pack) && decision.expert_pack.documents_pack.length > 0 ? (
                  <div className="mb-4 pb-4 border-b border-slate-700">
                    <div className="text-sm font-semibold text-gray-200 mb-2">④ 你需要准备什么（材料清单）</div>
                    <ul className="mt-2 list-disc pl-5 space-y-2 text-sm text-gray-300">
                      {decision.expert_pack.documents_pack.map((s: string, idx: number) => (
                        <li key={idx}>{s}</li>
                      ))}
                    </ul>
                  </div>
                ) : null}

                {decision.expert_pack.self_audit_checklist && Array.isArray(decision.expert_pack.self_audit_checklist) && decision.expert_pack.self_audit_checklist.length > 0 ? (
                  <div>
                    <div className="text-sm font-semibold text-gray-200 mb-2">自检表</div>
                    <ul className="mt-2 list-disc pl-5 space-y-2 text-sm text-gray-300">
                      {decision.expert_pack.self_audit_checklist.map((s: string, idx: number) => (
                        <li key={idx}>{s}</li>
                      ))}
                    </ul>
                  </div>
                ) : null}
                
                {/* ✅ 新增：决策版说明 */}
                <div className="mt-4 pt-4 border-t border-slate-700">
                  <p className="text-xs text-gray-400 italic">
                    这不是通用建议，而是基于你当前情况生成
                  </p>
                </div>
              </div>
            )}
          </>
        )}
        
        {/* 关于本评估（版本B：咨询前第一站定位） */}
        <div className="mt-6 pt-4 border-t border-slate-700/50">
          <div className="space-y-3">
            <div className="text-sm font-semibold text-gray-400 text-center">关于本评估</div>
            <div className="text-xs text-gray-500 text-center leading-relaxed space-y-2">
              <p>
                IberComply 用于在正式咨询前，<br />
                帮助你快速了解当前经营状态中的合规风险暴露情况。
              </p>
              <p>
                评估结果基于你填写的信息与风险模型生成，<br />
                仅作为风险识别与决策辅助参考，<br />
                不替代 gestoria / 律师的专业意见。
              </p>
              <div className="pt-1">
                <Link
                  href="/legal/disclaimer"
                  className="text-purple-400 hover:text-purple-300 underline inline-flex items-center gap-1"
                >
                  <span>📄</span>
                  <span>查看完整免责声明 →</span>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 底部固定 CTA（移动端） */}
      <div className="fixed bottom-0 left-0 right-0 border-t border-white/10 bg-black/80 backdrop-blur">
        <div className="mx-auto max-w-2xl px-4 py-3">
          <div className="flex gap-3">
            <button
              onClick={() => router.push("/assessment/start")}
              className="w-1/2 bg-slate-800/50 rounded-xl border border-slate-700 py-3 text-sm font-semibold text-gray-200"
            >
              再测一次
            </button>
            {requiredTier !== "none" && !isUnlocked ? (
              <button
                onClick={() => setShowPaySheet(true)}
                className="w-1/2 bg-gradient-to-r from-purple-600 to-cyan-600 text-white font-semibold py-3 rounded-xl hover:from-purple-700 hover:to-cyan-700 transition-all text-sm"
              >
                解锁建议
              </button>
            ) : (
              <button
                onClick={() => document.getElementById("paid-section")?.scrollIntoView({ behavior: "smooth" })}
                className="w-1/2 bg-gradient-to-r from-purple-600 to-cyan-600 text-white font-semibold py-3 rounded-xl hover:from-purple-700 hover:to-cyan-700 transition-all text-sm"
              >
                查看行动清单
              </button>
            )}
          </div>
          <div className="pt-1 text-[11px] text-gray-500">
            * 仅风险提示与材料准备建议，不构成法律/税务意见。
          </div>
        </div>
      </div>

      {/* BottomSheet（解锁确认）- ✅ 新版结构：€15内容列表 + 决策推荐€39 + 双按钮 */}
      {showPaySheet && (
        <div className="fixed inset-0 z-50">
          <div
            className="absolute inset-0 bg-black/60"
            onClick={() => setShowPaySheet(false)}
          />
          <div className="absolute bottom-0 left-0 right-0 rounded-t-2xl border border-white/10 bg-[#0B0F19] p-5 max-h-[90vh] overflow-y-auto">
            <div className="mx-auto max-w-2xl">
              <div className="flex items-start justify-between gap-3 mb-5">
                <div>
                  <div className="text-xl font-semibold">解锁完整判断依据</div>
                </div>
                <button
                  className="text-gray-400 hover:text-white"
                  onClick={() => setShowPaySheet(false)}
                >
                  ✕
                </button>
              </div>

              {/* €15 自查版内容列表 */}
              <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-4 mb-4">
                <div className="text-sm font-semibold text-gray-200 mb-3">✅ €15 自查版（Self-check）包含：</div>
                <ul className="space-y-2 text-sm text-gray-300">
                  <li className="flex items-start gap-2">
                    <span className="text-purple-400 mt-0.5">•</span>
                    <span><strong>阶段 + 解释失败点摘要</strong>：让你知道问题出在哪</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-purple-400 mt-0.5">•</span>
                    <span><strong>基础行动清单</strong>：可以直接照做</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-purple-400 mt-0.5">•</span>
                    <span><strong>基础 PDF</strong>：可交给 gestor/顾问</span>
                  </li>
                </ul>
              </div>

              {/* 分割线 */}
              <div className="flex items-center gap-3 my-4">
                <div className="flex-1 h-px bg-gradient-to-r from-transparent via-slate-600 to-transparent"></div>
              </div>

              {/* 🎯 决策推荐（转化关键） */}
              <div className="bg-gradient-to-br from-cyan-500/10 to-purple-500/10 rounded-xl border border-cyan-500/30 p-4 mb-4">
                <div className="text-sm font-semibold text-cyan-200 mb-2">🎯 决策推荐</div>
                <div className="text-xs text-gray-400 mb-3">
                  如果你不想自己研究这些细节：
                </div>
                <div className="text-sm font-semibold text-gray-200 mb-2">决策版 €39（一次到位）</div>
                <ul className="space-y-1.5 text-xs text-gray-300 mb-3">
                  <li className="flex items-start gap-2">
                    <span className="text-cyan-400 mt-0.5">✓</span>
                    <span>完整阶段解释（监管视角 + 你该做什么/不该做什么）</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-cyan-400 mt-0.5">✓</span>
                    <span>更完整的材料清单/自检表</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-cyan-400 mt-0.5">✓</span>
                    <span>是否需要找专业人士的决策提示（不做个案处理）</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-cyan-400 mt-0.5">✓</span>
                    <span>更完整的 30/90 天行动节奏</span>
                  </li>
                </ul>
                <div className="text-xs text-cyan-300 font-medium">
                  👉 决策版包含 €15 的全部内容
                </div>
                <div className="mt-2 text-xs text-gray-500">
                  本平台不提供法律/税务建议；涉及历史问题请咨询专业人士。
                </div>
              </div>

              {/* 底部双按钮 */}
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => handleUnlockConfirm("basic_15")}
                  className="bg-gradient-to-r from-purple-600 to-cyan-600 text-white font-semibold py-3 rounded-xl hover:from-purple-700 hover:to-cyan-700 transition-all text-sm"
                >
                  解锁 €15
                </button>
                <button
                  onClick={() => handleUnlockConfirm("expert_39")}
                  className="border-2 border-cyan-500/50 text-cyan-300 font-semibold py-3 rounded-xl hover:border-cyan-400 hover:bg-cyan-500/10 transition-all text-sm"
                >
                  升级决策版 €39
                </button>
              </div>

              <div className="mt-3 text-xs text-gray-500 text-center">
                我们不保存身份证信息；仅使用你填写的经营信息生成建议。
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ✅ 底部固定 CTA：basic_15 时显示 "升级决策版 €39" */}
      {unlockedTier === "basic_15" && isUnlocked && (
        <div className="fixed bottom-0 left-0 right-0 z-40 bg-slate-900/95 backdrop-blur-sm border-t border-slate-700 safe-bottom">
          <div className="max-w-2xl mx-auto px-4 py-3">
            <button
              onClick={() => handleUnlockConfirm("expert_39")}
              className="w-full bg-gradient-to-r from-purple-600 to-cyan-600 text-white font-semibold py-3 rounded-xl hover:from-purple-700 hover:to-cyan-700 transition-all text-sm"
            >
              升级决策版 €39
            </button>
          </div>
        </div>
      )}
        </div>
      </div>
    </Layout>
  );
}
