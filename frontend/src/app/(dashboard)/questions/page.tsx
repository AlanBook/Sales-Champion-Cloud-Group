"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/components/auth-provider";
import { LoadingState, PageHeader, Panel } from "@/components/ui-kit";
import { apiFetch } from "@/lib/api";
import type { ObjectionInsight, QuestionInsight } from "@/lib/types";

export default function QuestionsPage() {
  const { token } = useAuth();
  const [questions, setQuestions] = useState<QuestionInsight[]>([]);
  const [objections, setObjections] = useState<ObjectionInsight[]>([]);

  useEffect(() => {
    if (!token) return;
    Promise.all([
      apiFetch<QuestionInsight[]>("/dashboard/questions", token),
      apiFetch<ObjectionInsight[]>("/dashboard/objections", token),
    ]).then(([nextQuestions, nextObjections]) => {
      setQuestions(nextQuestions);
      setObjections(nextObjections);
    });
  }, [token]);

  if (!questions.length && !objections.length) {
    return <LoadingState label="问题与异议分析" />;
  }

  return (
    <div className="space-y-4">
      <PageHeader
        eyebrow="高频问题 / 高频异议"
        title="老板最该盯住的是团队哪里总接不住"
        description="把客户反复问的问题和高价异议集中起来，能更快决定该补商品知识、补话术，还是补收口动作。"
      />

      <div className="grid gap-4 xl:grid-cols-2">
        <Panel>
          <h3 className="text-lg font-semibold">高频客户问题</h3>
          <div className="mt-4 space-y-3">
            {questions.map((item) => (
              <div key={item.label} className="rounded-2xl border border-[var(--line)] bg-white/70 p-4">
                <div className="flex items-center justify-between gap-4">
                  <span>{item.label}</span>
                  <strong>{item.count}</strong>
                </div>
              </div>
            ))}
          </div>
        </Panel>

        <Panel>
          <h3 className="text-lg font-semibold">高频异议</h3>
          <div className="mt-4 space-y-3">
            {objections.map((item) => (
              <div key={item.type} className="rounded-2xl border border-[var(--line)] bg-white/70 p-4">
                <div className="flex items-center justify-between gap-4">
                  <span>{item.type}</span>
                  <strong>{item.count}</strong>
                </div>
              </div>
            ))}
          </div>
        </Panel>
      </div>
    </div>
  );
}
