"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/components/auth-provider";
import { LoadingState, PageHeader, Panel } from "@/components/ui-kit";
import { apiFetch } from "@/lib/api";
import type { ProductInsight } from "@/lib/types";

export default function ProductInsightsPage() {
  const { token } = useAuth();
  const [items, setItems] = useState<ProductInsight[]>([]);

  useEffect(() => {
    if (!token) return;
    apiFetch<ProductInsight[]>("/dashboard/product-insights", token).then(setItems);
  }, [token]);

  if (!items.length) {
    return <LoadingState label="商品洞察" />;
  }

  return (
    <div className="space-y-4">
      <PageHeader
        eyebrow="商品洞察"
        title="把热度和成交拆开看，才能知道商品问题还是导购问题"
        description="这一页用来识别哪些商品咨询特别高但订单跟不上，从而判断是商品表达、价格解释还是场景匹配出了问题。"
      />

      <div className="grid gap-4 xl:grid-cols-2">
        {items.map((item) => (
          <Panel key={item.product_id}>
            <div className="flex items-start justify-between gap-4">
              <div>
                <strong className="text-xl">{item.product_name}</strong>
                <p className="mt-2 text-sm leading-7 text-[var(--muted)]">
                  热度高说明被频繁推荐；若订单明显跟不上，老板就该盯话术、异议解释和预算匹配。
                </p>
              </div>
              <span className={`rounded-full px-3 py-2 text-sm ${item.low_conversion_risk ? "bg-red-100 text-red-700" : "bg-emerald-100 text-emerald-700"}`}>
                {item.low_conversion_risk ? "高咨询低成交" : "表现正常"}
              </span>
            </div>
            <div className="mt-5 grid grid-cols-2 gap-3">
              <div className="rounded-2xl border border-[var(--line)] bg-white/65 p-4">
                <p className="text-sm text-[var(--muted)]">咨询热度</p>
                <strong className="mt-2 block text-3xl">{item.heat}</strong>
              </div>
              <div className="rounded-2xl border border-[var(--line)] bg-white/65 p-4">
                <p className="text-sm text-[var(--muted)]">成交订单</p>
                <strong className="mt-2 block text-3xl">{item.paid_orders}</strong>
              </div>
            </div>
          </Panel>
        ))}
      </div>
    </div>
  );
}
