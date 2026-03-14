"use client";

import { useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/components/auth-provider";
import { SideNavLink } from "@/components/ui-kit";

const NAV_ITEMS = [
  { href: "/dashboard", label: "老板驾驶舱" },
  { href: "/ranking", label: "导购排行" },
  { href: "/questions", label: "问题与异议" },
  { href: "/product-insights", label: "商品洞察" },
  { href: "/knowledge", label: "知识库管理" },
  { href: "/assistant", label: "导购助手" },
  { href: "/training", label: "新人陪练" },
];

export function DashboardShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { ready, token, user, logout } = useAuth();

  useEffect(() => {
    if (!ready) {
      return;
    }
    if (!token) {
      router.replace("/login");
    }
  }, [ready, token, router]);

  if (!ready || !token) {
    return (
      <main className="flex min-h-screen items-center justify-center px-6">
        <div className="panel rounded-[2rem] px-6 py-8 text-center text-sm text-[var(--muted)]">
          正在检查登录状态...
        </div>
      </main>
    );
  }

  return (
    <div className="min-h-screen px-4 py-4 lg:px-6">
      <div className="mx-auto grid max-w-[1500px] gap-4 lg:grid-cols-[280px_minmax(0,1fr)]">
        <aside className="panel rounded-[2rem] p-5 lg:sticky lg:top-4 lg:h-[calc(100vh-2rem)]">
          <Link href="/dashboard" className="block rounded-[1.5rem] bg-[rgba(255,255,255,0.76)] p-4">
            <span className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,var(--leaf),var(--tea-700))] text-xl font-semibold text-white">
              冠
            </span>
            <div className="mt-4">
              <strong className="hero-serif block text-2xl">销冠云团</strong>
              <span className="mt-1 block text-xs uppercase tracking-[0.24em] text-[var(--muted)]">
                High-end Tea Demo
              </span>
            </div>
          </Link>

          <div className="mt-6 grid gap-2">
            {NAV_ITEMS.map((item) => (
              <SideNavLink key={item.href} href={item.href} label={item.label} />
            ))}
          </div>

          <div className="mt-6 rounded-[1.5rem] border border-[var(--line)] bg-white/65 p-4">
            <p className="text-xs uppercase tracking-[0.22em] text-[var(--muted)]">当前身份</p>
            <strong className="mt-2 block text-lg">{user?.display_name ?? "演示用户"}</strong>
            <p className="mt-1 text-sm text-[var(--muted)]">
              {user?.role_code === "boss" ? "老板 / 经营负责人" : user?.role_code}
            </p>
            <button
              type="button"
              onClick={() => {
                logout();
                router.replace("/login");
              }}
              className="mt-4 w-full rounded-2xl bg-[var(--tea-900)] px-4 py-3 text-sm text-white"
            >
              退出登录
            </button>
          </div>
        </aside>

        <main className="space-y-4">
          <header className="panel rounded-[2rem] px-5 py-4">
            <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.24em] text-[var(--muted)]">当前页面</p>
                <strong className="mt-2 block text-2xl">
                  {NAV_ITEMS.find((item) => pathname.startsWith(item.href))?.label ?? "销冠云团"}
                </strong>
              </div>
              <div className="flex flex-wrap gap-2 text-sm text-[var(--muted)]">
                <span className="rounded-full border border-[var(--line)] bg-white/70 px-3 py-2">
                  高端茶 Demo 边界
                </span>
                <span className="rounded-full border border-[var(--line)] bg-white/70 px-3 py-2">
                  真实数据库驱动
                </span>
                <span className="rounded-full border border-[var(--line)] bg-white/70 px-3 py-2">
                  evidence sources 可追踪
                </span>
              </div>
            </div>
          </header>
          {children}
        </main>
      </div>
    </div>
  );
}
