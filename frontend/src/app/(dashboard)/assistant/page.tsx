"use client";

import { useState } from "react";
import { useAuth } from "@/components/auth-provider";
import { EmptyState, PageHeader, Panel, Pill } from "@/components/ui-kit";
import { apiFetch } from "@/lib/api";
import type { AssistantResponse } from "@/lib/types";

export default function AssistantPage() {
  const { token, user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AssistantResponse | null>(null);
  const [form, setForm] = useState({
    customer_message: "送领导，1500 左右预算，想体面一点。",
    scene_hint: "gift_leader",
    budget_range: "500-1500",
    taste_preference: "醇厚",
  });

  return (
    <div className="space-y-4">
      <PageHeader
        eyebrow="导购销冠助手"
        title="客户信息输入在左，推荐结果、话术和证据来源在右"
        description="这个页面专门服务一线导购。目标不是自由聊天，而是让导购在接待过程中快速获得推荐、价值解释、异议处理和继续追问。"
      />

      <div className="grid gap-4 xl:grid-cols-[0.92fr_1.08fr]">
        <Panel>
          <h3 className="text-lg font-semibold">客户需求输入</h3>
          <div className="mt-4 space-y-4">
            <textarea
              value={form.customer_message}
              onChange={(event) => setForm((current) => ({ ...current, customer_message: event.target.value }))}
              className="min-h-[160px] w-full rounded-2xl border border-[var(--line)] bg-white/80 px-4 py-3"
            />
            <div className="grid gap-3 lg:grid-cols-3">
              <input
                value={form.scene_hint}
                onChange={(event) => setForm((current) => ({ ...current, scene_hint: event.target.value }))}
                className="rounded-2xl border border-[var(--line)] bg-white/80 px-4 py-3"
              />
              <input
                value={form.budget_range}
                onChange={(event) => setForm((current) => ({ ...current, budget_range: event.target.value }))}
                className="rounded-2xl border border-[var(--line)] bg-white/80 px-4 py-3"
              />
              <input
                value={form.taste_preference}
                onChange={(event) => setForm((current) => ({ ...current, taste_preference: event.target.value }))}
                className="rounded-2xl border border-[var(--line)] bg-white/80 px-4 py-3"
              />
            </div>
            <button
              type="button"
              disabled={loading || !token || !user}
              onClick={async () => {
                if (!token || !user) return;
                setLoading(true);
                const payload = await apiFetch<AssistantResponse>("/assistant/recommend", token, {
                  method: "POST",
                  body: JSON.stringify({
                    staff_id: user.id,
                    customer_id: null,
                    session_id: null,
                    input: {
                      customer_message: form.customer_message,
                      scene_hint: form.scene_hint,
                      budget_range: form.budget_range,
                      taste_preference: form.taste_preference
                        .split(/[，,]/)
                        .map((item) => item.trim())
                        .filter(Boolean),
                    },
                  }),
                });
                setResult(payload);
                setLoading(false);
              }}
              className="w-full rounded-2xl bg-[linear-gradient(135deg,var(--leaf),var(--tea-700))] px-4 py-4 text-white"
            >
              {loading ? "正在生成推荐..." : "生成结构化推荐"}
            </button>
          </div>
        </Panel>

        <Panel>
          {result ? (
            <div className="space-y-4">
              <div className="flex flex-wrap gap-2">
                <Pill>{result.result.customer_intent}</Pill>
                <Pill>{result.result.scene}</Pill>
                <Pill>{result.result.budget_range}</Pill>
                <Pill>confidence {result.result.confidence}</Pill>
              </div>

              <article className="rounded-2xl border border-[var(--line)] bg-white/70 p-4">
                <h3 className="text-lg font-semibold">推荐商品</h3>
                <div className="mt-4 space-y-3">
                  {result.result.recommended_products.map((item) => (
                    <div key={item.product_id} className="rounded-2xl border border-[var(--line)] bg-[rgba(255,255,255,0.76)] p-4">
                      <div className="flex items-center justify-between gap-3">
                        <strong>{item.product_name}</strong>
                        <Pill>{Math.round(item.fit_score * 100)}%</Pill>
                      </div>
                      <p className="mt-3 text-sm leading-7 text-[var(--muted)]">{item.suggested_pitch}</p>
                      <div className="mt-3 flex flex-wrap gap-2">
                        {item.reason_points.map((point) => (
                          <Pill key={point}>{point}</Pill>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </article>

              <article className="rounded-2xl border border-[var(--line)] bg-white/70 p-4">
                <h3 className="text-lg font-semibold">推荐理由 / 异议处理 / 跟进问题</h3>
                <p className="mt-3 text-sm leading-7 text-[var(--muted)]">{result.result.suggested_pitch}</p>
                <ul className="mt-4 space-y-2 text-sm leading-7 text-[var(--muted)]">
                  {result.result.recommendation_reasons.map((item) => (
                    <li key={item}>• {item}</li>
                  ))}
                </ul>
                <div className="mt-4 rounded-2xl border border-[var(--line)] bg-[rgba(255,248,240,0.9)] p-4">
                  <strong>异议处理：{result.result.objection_strategy.type}</strong>
                  <p className="mt-2 text-sm leading-7 text-[var(--muted)]">
                    {result.result.objection_strategy.suggested_pitch}
                  </p>
                </div>
                <div className="mt-4 flex flex-wrap gap-2">
                  {result.result.follow_up_questions.map((item) => (
                    <Pill key={item}>{item}</Pill>
                  ))}
                </div>
              </article>

              <article className="rounded-2xl border border-[var(--line)] bg-white/70 p-4">
                <h3 className="text-lg font-semibold">Evidence Sources</h3>
                <div className="mt-3 flex flex-wrap gap-2">
                  {result.result.evidence_sources.map((item) => (
                    <Pill key={item}>{item}</Pill>
                  ))}
                </div>
              </article>
            </div>
          ) : (
            <EmptyState
              title="还没有推荐结果"
              description="先用“送领导 1500 左右预算，想体面一点”或“为什么这款茶这么贵”试跑，确认结构化推荐、话术、异议处理和证据来源都能一起出来。"
            />
          )}
        </Panel>
      </div>
    </div>
  );
}
