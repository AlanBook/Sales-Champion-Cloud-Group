"use client";

import { useState } from "react";
import { useAuth } from "@/components/auth-provider";
import { EmptyState, PageHeader, Panel } from "@/components/ui-kit";
import { apiFetch } from "@/lib/api";
import type { TrainingResult } from "@/lib/types";

export default function TrainingPage() {
  const { token, user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<TrainingResult | null>(null);
  const [scenario, setScenario] = useState({
    scene: "self_drink",
    customer_message: "平时自己喝，口感清一点，预算 500 以内。",
    sales_reply: "您可以看看我们这款高山白茶，比较顺口，也比较适合日常喝。",
  });

  return (
    <div className="space-y-4">
      <PageHeader
        eyebrow="新人陪练"
        title="让新人更快接近销冠，不靠抽象培训，靠真实接待动作"
        description="输入客户场景和销售回答后，系统会给总分、维度分、缺失提问和改写建议，方便店长拿来带教。"
      />

      <div className="grid gap-4 xl:grid-cols-[0.92fr_1.08fr]">
        <Panel>
          <h3 className="text-lg font-semibold">陪练输入</h3>
          <div className="mt-4 space-y-4">
            <input
              value={scenario.scene}
              onChange={(event) => setScenario((current) => ({ ...current, scene: event.target.value }))}
              className="w-full rounded-2xl border border-[var(--line)] bg-white/80 px-4 py-3"
            />
            <textarea
              value={scenario.customer_message}
              onChange={(event) => setScenario((current) => ({ ...current, customer_message: event.target.value }))}
              className="min-h-[120px] w-full rounded-2xl border border-[var(--line)] bg-white/80 px-4 py-3"
            />
            <textarea
              value={scenario.sales_reply}
              onChange={(event) => setScenario((current) => ({ ...current, sales_reply: event.target.value }))}
              className="min-h-[180px] w-full rounded-2xl border border-[var(--line)] bg-white/80 px-4 py-3"
            />
            <button
              type="button"
              disabled={!token || !user || loading}
              onClick={async () => {
                if (!token || !user) return;
                setLoading(true);
                const payload = await apiFetch<TrainingResult>("/training/evaluate", token, {
                  method: "POST",
                  body: JSON.stringify({
                    staff_id: user.id,
                    scenario: {
                      scene: scenario.scene,
                      customer_message: scenario.customer_message,
                    },
                    sales_reply: scenario.sales_reply,
                  }),
                });
                setResult(payload);
                setLoading(false);
              }}
              className="w-full rounded-2xl bg-[linear-gradient(135deg,var(--leaf),var(--tea-700))] px-4 py-4 text-white"
            >
              {loading ? "评分中..." : "生成陪练反馈"}
            </button>
          </div>
        </Panel>

        <Panel>
          {result ? (
            <div className="space-y-4">
              <div className="rounded-[1.8rem] border border-[var(--line)] bg-white/70 p-4">
                <p className="text-sm text-[var(--muted)]">总分</p>
                <strong className="hero-serif mt-3 block text-5xl">{result.score}</strong>
              </div>

              <div className="grid gap-3 lg:grid-cols-2">
                {Object.entries(result.dimension_scores).map(([key, value]) => (
                  <div key={key} className="rounded-2xl border border-[var(--line)] bg-white/70 p-4">
                    <p className="text-sm text-[var(--muted)]">{key}</p>
                    <strong className="mt-2 block text-3xl">{value}</strong>
                  </div>
                ))}
              </div>

              <article className="rounded-2xl border border-[var(--line)] bg-white/70 p-4">
                <h3 className="text-lg font-semibold">缺失提问</h3>
                <ul className="mt-3 space-y-2 text-sm leading-7 text-[var(--muted)]">
                  {result.missing_questions.map((item) => (
                    <li key={item}>• {item}</li>
                  ))}
                </ul>
              </article>

              <article className="rounded-2xl border border-[var(--line)] bg-white/70 p-4">
                <h3 className="text-lg font-semibold">改进建议</h3>
                <ul className="mt-3 space-y-2 text-sm leading-7 text-[var(--muted)]">
                  {result.improvement_suggestions.map((item) => (
                    <li key={item}>• {item}</li>
                  ))}
                </ul>
                <div className="mt-4 rounded-2xl border border-[var(--line)] bg-[rgba(255,248,240,0.9)] p-4 text-sm leading-7 text-[var(--muted)]">
                  {result.rewritten_reply}
                </div>
              </article>
            </div>
          ) : (
            <EmptyState title="还没有陪练结果" description="先用自饮场景跑一遍，再切送领导场景，店长就能讲清新人为什么接不住。" />
          )}
        </Panel>
      </div>
    </div>
  );
}
