"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { useAuth } from "@/components/auth-provider";
import { LoadingState, PageHeader, Panel, Pill } from "@/components/ui-kit";
import { apiFetch } from "@/lib/api";
import type { ChampionDetail } from "@/lib/types";

export default function ChampionDetailPage() {
  const params = useParams<{ staffId: string }>();
  const { token } = useAuth();
  const [detail, setDetail] = useState<ChampionDetail | null>(null);

  useEffect(() => {
    if (!token || !params.staffId) return;
    apiFetch<ChampionDetail>(`/dashboard/champion/${params.staffId}`, token).then(setDetail);
  }, [params.staffId, token]);

  if (!detail) {
    return <LoadingState label="销冠详情" />;
  }

  return (
    <div className="space-y-4">
      <PageHeader
        eyebrow="个人能力雷达"
        title={`${detail.name} 的销冠指数详情`}
        description="这里把一级维度分数、诊断建议和雷达数据拆出来，方便老板和店长做带教与复制。"
        extra={<Pill>{detail.role_level}</Pill>}
      />

      <div className="grid gap-4 xl:grid-cols-[1fr_0.9fr]">
        <Panel>
          <h3 className="text-lg font-semibold">能力维度</h3>
          <div className="mt-4 space-y-3">
            {detail.radar.map((item) => (
              <div key={item.dimension} className="rounded-2xl border border-[var(--line)] bg-white/65 p-4">
                <div className="flex items-center justify-between">
                  <span>{item.dimension}</span>
                  <strong>{item.score.toFixed(1)}</strong>
                </div>
                <div className="mt-3 h-3 rounded-full bg-[rgba(95,69,49,0.08)]">
                  <div
                    className="h-full rounded-full bg-[linear-gradient(135deg,var(--leaf),var(--gold))]"
                    style={{ width: `${Math.min(item.score, 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </Panel>

        <Panel>
          <h3 className="text-lg font-semibold">诊断建议</h3>
          <strong className="hero-serif mt-4 block text-4xl">{detail.total_score.toFixed(1)}</strong>
          <p className="mt-2 text-sm text-[var(--muted)]">总分越高，说明导购越接近“能接、能推、能转、能做高客单”的销冠形态。</p>
          <div className="mt-5 space-y-3">
            {detail.diagnostics.map((item) => (
              <article key={item} className="rounded-2xl border border-[var(--line)] bg-white/70 p-4 text-sm leading-7 text-[var(--muted)]">
                {item}
              </article>
            ))}
          </div>
        </Panel>
      </div>
    </div>
  );
}
