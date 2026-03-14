"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useAuth } from "@/components/auth-provider";
import { LoadingState, PageHeader, Panel, Pill } from "@/components/ui-kit";
import { apiFetch } from "@/lib/api";
import type { RankingItem } from "@/lib/types";

export default function RankingPage() {
  const { token } = useAuth();
  const [items, setItems] = useState<RankingItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    apiFetch<{ items: RankingItem[] }>("/dashboard/champion-ranking", token)
      .then((payload) => setItems(payload.items))
      .finally(() => setLoading(false));
  }, [token]);

  if (loading) {
    return <LoadingState label="导购排行" />;
  }

  return (
    <div className="space-y-4">
      <PageHeader
        eyebrow="销冠指数"
        title="导购排行不是只看 GMV，而是看能力结构"
        description="基于接待能力、推荐能力、转化能力、成交价值四个一级维度计算销冠指数，支持老板快速识别谁值得复制、谁需要补训练。"
      />

      <div className="grid gap-4">
        {items.map((item, index) => (
          <Panel key={item.staff_id} className="overflow-hidden">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="text-sm text-[var(--muted)]">NO. {index + 1}</p>
                <div className="mt-2 flex items-center gap-3">
                  <strong className="text-2xl">{item.name}</strong>
                  <Pill>{item.level}</Pill>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <p className="text-sm text-[var(--muted)]">总分</p>
                  <strong className="hero-serif text-4xl">{item.total_score.toFixed(1)}</strong>
                </div>
                <Link
                  href={`/ranking/${item.staff_id}`}
                  className="rounded-2xl bg-[var(--tea-900)] px-4 py-3 text-sm text-white"
                >
                  看详情
                </Link>
              </div>
            </div>

            <div className="mt-5 grid gap-3 lg:grid-cols-4">
              {Object.entries(item.dimensions).map(([key, value]) => (
                <div key={key} className="rounded-2xl border border-[var(--line)] bg-white/65 p-4">
                  <p className="text-sm text-[var(--muted)]">{key}</p>
                  <strong className="mt-3 block text-2xl">{value.toFixed(1)}</strong>
                </div>
              ))}
            </div>
          </Panel>
        ))}
      </div>
    </div>
  );
}
