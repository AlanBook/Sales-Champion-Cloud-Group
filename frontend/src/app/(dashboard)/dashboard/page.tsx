"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/components/auth-provider";
import { EmptyState, LoadingState, MetricCard, PageHeader, Panel } from "@/components/ui-kit";
import { apiFetch } from "@/lib/api";
import type {
  ObjectionInsight,
  OverviewResponse,
  ProductInsight,
  QuestionInsight,
  TeamWeakness,
} from "@/lib/types";

export default function DashboardPage() {
  const { token } = useAuth();
  const [loading, setLoading] = useState(true);
  const [overview, setOverview] = useState<OverviewResponse | null>(null);
  const [questions, setQuestions] = useState<QuestionInsight[]>([]);
  const [objections, setObjections] = useState<ObjectionInsight[]>([]);
  const [products, setProducts] = useState<ProductInsight[]>([]);
  const [weaknesses, setWeaknesses] = useState<TeamWeakness[]>([]);

  useEffect(() => {
    if (!token) return;
    Promise.all([
      apiFetch<OverviewResponse>("/dashboard/overview", token),
      apiFetch<QuestionInsight[]>("/dashboard/questions", token),
      apiFetch<ObjectionInsight[]>("/dashboard/objections", token),
      apiFetch<ProductInsight[]>("/dashboard/product-insights", token),
      apiFetch<TeamWeakness[]>("/dashboard/team-weaknesses", token),
    ])
      .then(([nextOverview, nextQuestions, nextObjections, nextProducts, nextWeaknesses]) => {
        setOverview(nextOverview);
        setQuestions(nextQuestions);
        setObjections(nextObjections);
        setProducts(nextProducts);
        setWeaknesses(nextWeaknesses);
      })
      .finally(() => setLoading(false));
  }, [token]);

  if (loading) {
    return <LoadingState label="老板驾驶舱" />;
  }

  if (!overview) {
    return <EmptyState title="暂无经营数据" description="请先加载演示种子数据或检查后端服务。" />;
  }

  return (
    <div className="space-y-4">
      <PageHeader
        eyebrow="老板端 CEO 驾驶舱"
        title="一屏看清团队接待、成交、异议和商品热度"
        description="这里不是聊天页，而是把导购接待、推荐、订单、异议和销冠指数回流成经营洞察的老板视角。"
      />

      <div className="grid gap-4 xl:grid-cols-4">
        <MetricCard label="今日接待数" value={`${overview.today_reception_count}`} hint="来自当日会话 session" />
        <MetricCard label="今日成交数" value={`${overview.today_conversion_count}`} hint="paid 订单数" />
        <MetricCard label="今日成交额" value={`¥ ${overview.today_revenue.toLocaleString()}`} hint="真实订单金额汇总" />
        <MetricCard label="本周转化率" value={`${Math.round(overview.week_conversion_rate * 100)}%`} hint="converted / reception" />
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <Panel>
          <h3 className="text-lg font-semibold">团队销冠排行</h3>
          <div className="mt-4 space-y-3">
            {overview.top_staff.map((item, index) => (
              <div key={item.staff_id} className="rounded-2xl border border-[var(--line)] bg-white/70 px-4 py-3">
                <div className="flex items-center justify-between">
                  <span>{index + 1}. {item.name}</span>
                  <strong>{item.score.toFixed(1)}</strong>
                </div>
              </div>
            ))}
          </div>
        </Panel>

        <Panel>
          <h3 className="text-lg font-semibold">高频异议</h3>
          <div className="mt-4 space-y-3">
            {objections.map((item) => (
              <div key={item.type} className="rounded-2xl border border-[var(--line)] bg-white/70 px-4 py-3">
                <div className="flex items-center justify-between">
                  <span>{item.type}</span>
                  <strong>{item.count}</strong>
                </div>
              </div>
            ))}
          </div>
        </Panel>

        <Panel>
          <h3 className="text-lg font-semibold">高频客户问题</h3>
          <div className="mt-4 space-y-3">
            {questions.map((item) => (
              <div key={item.label} className="rounded-2xl border border-[var(--line)] bg-white/70 px-4 py-3">
                <div className="flex items-center justify-between gap-4">
                  <span>{item.label}</span>
                  <strong>{item.count}</strong>
                </div>
              </div>
            ))}
          </div>
        </Panel>
      </div>

      <div className="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
        <Panel>
          <h3 className="text-lg font-semibold">商品热度与高咨询低成交</h3>
          <div className="mt-4 overflow-hidden rounded-[1.25rem] border border-[var(--line)]">
            <table className="min-w-full text-sm">
              <thead className="bg-white/65 text-left text-[var(--muted)]">
                <tr>
                  <th className="px-4 py-3">商品</th>
                  <th className="px-4 py-3">咨询热度</th>
                  <th className="px-4 py-3">成交订单</th>
                  <th className="px-4 py-3">风险</th>
                </tr>
              </thead>
              <tbody>
                {products.slice(0, 8).map((item) => (
                  <tr key={item.product_id} className="border-t border-[var(--line)] bg-white/45">
                    <td className="px-4 py-3">{item.product_name}</td>
                    <td className="px-4 py-3">{item.heat}</td>
                    <td className="px-4 py-3">{item.paid_orders}</td>
                    <td className="px-4 py-3">
                      {item.low_conversion_risk ? (
                        <span className="rounded-full bg-red-100 px-3 py-1 text-red-700">高咨询低成交</span>
                      ) : (
                        <span className="rounded-full bg-emerald-100 px-3 py-1 text-emerald-700">表现正常</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>

        <Panel>
          <h3 className="text-lg font-semibold">团队短板建议</h3>
          <div className="mt-4 space-y-3">
            {weaknesses.map((item) => (
              <article key={item.dimension} className="rounded-2xl border border-[var(--line)] bg-white/70 p-4">
                <div className="flex items-center justify-between">
                  <strong>{item.dimension}</strong>
                  <span className="text-sm text-[var(--muted)]">{item.score.toFixed(1)}</span>
                </div>
                <p className="mt-2 text-sm leading-7 text-[var(--muted)]">{item.suggestion}</p>
              </article>
            ))}
          </div>
        </Panel>
      </div>
    </div>
  );
}
