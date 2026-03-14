"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

export function PageHeader({
  eyebrow,
  title,
  description,
  extra,
}: {
  eyebrow: string;
  title: string;
  description: string;
  extra?: ReactNode;
}) {
  return (
    <div className="flex flex-col gap-4 rounded-[2rem] border border-[var(--line)] bg-[rgba(255,248,240,0.86)] p-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <span className="inline-flex rounded-full border border-[rgba(93,117,85,0.15)] bg-[rgba(93,117,85,0.1)] px-3 py-1 text-sm text-[var(--leaf)]">
          {eyebrow}
        </span>
        <h1 className="hero-serif mt-4 text-4xl leading-tight lg:text-5xl">{title}</h1>
        <p className="mt-3 max-w-3xl text-[15px] leading-7 text-[var(--muted)]">
          {description}
        </p>
      </div>
      {extra ? <div className="flex flex-wrap gap-3">{extra}</div> : null}
    </div>
  );
}

export function Panel({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return <section className={`panel rounded-[1.75rem] p-5 ${className}`}>{children}</section>;
}

export function MetricCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: string;
  hint: string;
}) {
  return (
    <Panel>
      <p className="text-sm text-[var(--muted)]">{label}</p>
      <strong className="hero-serif mt-4 block text-4xl">{value}</strong>
      <p className="mt-3 text-sm text-[var(--muted)]">{hint}</p>
    </Panel>
  );
}

export function Pill({ children }: { children: ReactNode }) {
  return (
    <span className="inline-flex rounded-full border border-[var(--line)] bg-white/70 px-3 py-1 text-sm text-[var(--muted)]">
      {children}
    </span>
  );
}

export function SideNavLink({
  href,
  label,
}: {
  href: string;
  label: string;
}) {
  const pathname = usePathname();
  const active = pathname === href || pathname.startsWith(`${href}/`);
  return (
    <Link
      href={href}
      className={`rounded-2xl px-4 py-3 text-sm transition ${
        active
          ? "bg-[linear-gradient(135deg,rgba(93,117,85,0.95),rgba(143,102,70,0.95))] text-white shadow-lg"
          : "border border-[var(--line)] bg-white/60 text-[var(--tea-900)] hover:-translate-y-0.5"
      }`}
    >
      {label}
    </Link>
  );
}

export function LoadingState({ label }: { label: string }) {
  return (
    <div className="panel rounded-[1.5rem] p-6 text-sm text-[var(--muted)]">
      正在加载 {label}...
    </div>
  );
}

export function EmptyState({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <Panel>
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="mt-2 text-sm leading-7 text-[var(--muted)]">{description}</p>
    </Panel>
  );
}
