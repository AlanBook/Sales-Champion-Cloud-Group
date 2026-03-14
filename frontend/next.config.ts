import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 默认配置（用于本地开发和 Vercel 部署）
  // GitHub Pages 部署需要静态导出，但有动态路由限制
  // 建议使用 Vercel 部署（见 vercel.json 和部署指南.md）
};

export default nextConfig;
