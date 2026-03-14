"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/auth-provider";

export default function LoginPage() {
  const router = useRouter();
  const { ready, token, login } = useAuth();
  const [username, setUsername] = useState("boss_demo");
  const [password, setPassword] = useState("password");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (ready && token) {
      router.replace("/dashboard");
    }
  }, [ready, token, router]);

  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-10">
      <div className="grid w-full max-w-6xl gap-6 lg:grid-cols-[1.05fr_0.95fr]">
        <section className="panel rounded-[2.5rem] p-7 lg:p-10">
          <span className="inline-flex rounded-full border border-[rgba(93,117,85,0.15)] bg-[rgba(93,117,85,0.1)] px-4 py-2 text-sm text-[var(--leaf)]">
            老板驾驶舱 × 导购销冠助手 × 知识沉淀底座
          </span>
          <h1 className="hero-serif mt-6 text-5xl leading-tight lg:text-6xl">
            让老板看清团队，让导购现场更像销冠
          </h1>
          <p className="mt-5 max-w-2xl text-[17px] leading-8 text-[var(--muted)]">
            这是面向高端茶场景的销售操作系统演示版。前台能做客户需求识别、场景化推荐、
            高价异议处理；后台能看经营总览、导购排行、商品热度和团队短板。
          </p>

          <div className="mt-8 grid gap-4 sm:grid-cols-3">
            {[
              ["老板驾驶舱", "经营总览、排行、商品热度、高咨询低成交识别"],
              ["导购助手", "结构化推荐、话术、异议处理、evidence sources"],
              ["新人陪练", "评分、缺失提问、改写建议"],
            ].map(([title, copy]) => (
              <article key={title} className="rounded-[1.8rem] border border-[var(--line)] bg-white/70 p-4">
                <strong>{title}</strong>
                <p className="mt-2 text-sm leading-7 text-[var(--muted)]">{copy}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="panel rounded-[2.5rem] p-7 lg:p-10">
          <p className="text-xs uppercase tracking-[0.24em] text-[var(--muted)]">Demo Login</p>
          <h2 className="hero-serif mt-4 text-4xl">进入销冠云团</h2>
          <p className="mt-3 text-sm leading-7 text-[var(--muted)]">
            默认内置 `boss_demo / password`。如需看知识库写入动作，也可以改用
            `manager_demo / password`。
          </p>

          <form
            className="mt-8 space-y-4"
            onSubmit={async (event) => {
              event.preventDefault();
              setSubmitting(true);
              setError(null);
              try {
                await login(username, password);
                router.replace("/dashboard");
              } catch (nextError) {
                setError(nextError instanceof Error ? nextError.message : "登录失败");
              } finally {
                setSubmitting(false);
              }
            }}
          >
            <label className="block">
              <span className="mb-2 block text-sm text-[var(--muted)]">用户名</span>
              <input
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                className="w-full rounded-2xl border border-[var(--line)] bg-white/80 px-4 py-3 outline-none"
              />
            </label>

            <label className="block">
              <span className="mb-2 block text-sm text-[var(--muted)]">密码</span>
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="w-full rounded-2xl border border-[var(--line)] bg-white/80 px-4 py-3 outline-none"
              />
            </label>

            {error ? (
              <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {error}
              </div>
            ) : null}

            <button
              type="submit"
              disabled={submitting}
              className="w-full rounded-2xl bg-[linear-gradient(135deg,var(--leaf),var(--tea-700))] px-4 py-4 text-white"
            >
              {submitting ? "登录中..." : "进入系统"}
            </button>
          </form>

          <div className="mt-8 rounded-[1.8rem] border border-[var(--line)] bg-white/65 p-4 text-sm leading-7 text-[var(--muted)]">
            <strong className="text-[var(--tea-900)]">路演建议</strong>
            <p className="mt-2">先进入老板驾驶舱讲痛点，再切到导购助手跑“送领导”“为什么贵”两个场景，最后回到 Dashboard 看回流洞察。</p>
          </div>
        </section>
      </div>
    </main>
  );
}
