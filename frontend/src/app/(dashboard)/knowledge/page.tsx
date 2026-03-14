"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/components/auth-provider";
import { EmptyState, LoadingState, PageHeader, Panel, Pill } from "@/components/ui-kit";
import { apiFetch } from "@/lib/api";
import type { KnowledgeDocument, KnowledgeSearchItem } from "@/lib/types";

const DEFAULT_QUERY = "送领导怎么选更稳妥";

export default function KnowledgePage() {
  const { token, user } = useAuth();
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);
  const [results, setResults] = useState<KnowledgeSearchItem[]>([]);
  const [query, setQuery] = useState(DEFAULT_QUERY);
  const [ingestOpen, setIngestOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({
    doc_type: "faq",
    title: "新增知识文档",
    content: "这里填写 FAQ、话术、案例或策略文档内容。",
  });

  useEffect(() => {
    if (!token) return;
    apiFetch<KnowledgeDocument[]>("/knowledge/documents", token).then(setDocuments);
  }, [token]);

  const search = async () => {
    if (!token) return;
    const payload = await apiFetch<{ items: KnowledgeSearchItem[] }>(
      `/knowledge/search?q=${encodeURIComponent(query)}&top_k=6`,
      token,
    );
    setResults(payload.items);
  };

  useEffect(() => {
    if (!token) {
      return;
    }
    let cancelled = false;
    apiFetch<{ items: KnowledgeSearchItem[] }>(
      `/knowledge/search?q=${encodeURIComponent(DEFAULT_QUERY)}&top_k=6`,
      token,
    ).then((payload) => {
      if (!cancelled) {
        setResults(payload.items);
      }
    });
    return () => {
      cancelled = true;
    };
  }, [token]);

  if (!documents.length) {
    return <LoadingState label="知识库管理" />;
  }

  return (
    <div className="space-y-4">
      <PageHeader
        eyebrow="知识库底座"
        title="商品、FAQ、销冠案例和异议案例都回到一个可检索底座"
        description="导购助手的 evidence sources 来自这里。知识库页既要能给管理者看文档分布，也要能直接做检索和导入。"
        extra={
          <button
            type="button"
            onClick={() => setIngestOpen((current) => !current)}
            className="rounded-2xl bg-[var(--tea-900)] px-4 py-3 text-sm text-white"
          >
            {ingestOpen ? "收起导入" : "新增文档"}
          </button>
        }
      />

      {ingestOpen ? (
        <Panel>
          <h3 className="text-lg font-semibold">导入知识文档</h3>
          <p className="mt-2 text-sm text-[var(--muted)]">
            当前登录角色：{user?.display_name}。建议使用 `manager_demo` 或 `admin_demo` 演示写入。
          </p>
          <div className="mt-4 grid gap-3 lg:grid-cols-3">
            <input
              value={form.doc_type}
              onChange={(event) => setForm((current) => ({ ...current, doc_type: event.target.value }))}
              className="rounded-2xl border border-[var(--line)] bg-white/80 px-4 py-3"
            />
            <input
              value={form.title}
              onChange={(event) => setForm((current) => ({ ...current, title: event.target.value }))}
              className="rounded-2xl border border-[var(--line)] bg-white/80 px-4 py-3"
            />
            <button
              type="button"
              disabled={submitting}
              onClick={async () => {
                if (!token) return;
                setSubmitting(true);
                await apiFetch("/knowledge/ingest", token, {
                  method: "POST",
                  body: JSON.stringify({
                    doc_type: form.doc_type,
                    title: form.title,
                    content: form.content,
                    metadata: { source: "frontend-demo" },
                    source_type: "manual",
                  }),
                }).catch(() => undefined);
                const docs = await apiFetch<KnowledgeDocument[]>("/knowledge/documents", token);
                setDocuments(docs);
                setSubmitting(false);
              }}
              className="rounded-2xl bg-[linear-gradient(135deg,var(--leaf),var(--tea-700))] px-4 py-3 text-white"
            >
              {submitting ? "导入中..." : "提交导入"}
            </button>
          </div>
          <textarea
            value={form.content}
            onChange={(event) => setForm((current) => ({ ...current, content: event.target.value }))}
            className="mt-3 min-h-[140px] w-full rounded-2xl border border-[var(--line)] bg-white/80 px-4 py-3"
          />
        </Panel>
      ) : null}

      <div className="grid gap-4 xl:grid-cols-[0.92fr_1.08fr]">
        <Panel>
          <div className="flex items-center justify-between gap-3">
            <h3 className="text-lg font-semibold">文档列表</h3>
            <Pill>{documents.length} 份文档</Pill>
          </div>
          <div className="mt-4 space-y-3">
            {documents.slice(0, 14).map((item) => (
              <article key={item.id} className="rounded-2xl border border-[var(--line)] bg-white/70 p-4">
                <div className="flex items-center justify-between gap-4">
                  <strong>{item.title}</strong>
                  <Pill>{item.doc_type}</Pill>
                </div>
                <p className="mt-2 text-sm leading-7 text-[var(--muted)]">{item.summary}</p>
              </article>
            ))}
          </div>
        </Panel>

        <Panel>
          <div className="flex flex-col gap-3 lg:flex-row">
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              className="flex-1 rounded-2xl border border-[var(--line)] bg-white/80 px-4 py-3"
            />
            <button
              type="button"
              onClick={() => void search()}
              className="rounded-2xl bg-[var(--tea-900)] px-4 py-3 text-white"
            >
              检索知识库
            </button>
          </div>

          <div className="mt-5 space-y-3">
            {results.length ? (
              results.map((item) => (
                <article key={item.chunk_id} className="rounded-2xl border border-[var(--line)] bg-white/70 p-4">
                  <div className="flex items-center justify-between gap-4">
                    <strong>{item.title}</strong>
                    <Pill>{item.doc_type}</Pill>
                  </div>
                  <p className="mt-2 text-sm leading-7 text-[var(--muted)]">{item.content}</p>
                  <p className="mt-3 text-xs uppercase tracking-[0.22em] text-[var(--muted)]">
                    score {item.score.toFixed(2)} / {item.source_ref ?? item.document_id}
                  </p>
                </article>
              ))
            ) : (
              <EmptyState title="暂无检索结果" description="换一个更具体的问题，例如“送领导更稳妥的礼盒”或“高价异议怎么解释”。" />
            )}
          </div>
        </Panel>
      </div>
    </div>
  );
}
