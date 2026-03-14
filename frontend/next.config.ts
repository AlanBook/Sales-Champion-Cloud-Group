import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // GitHub Pages 部署配置
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
  // 生产环境 API 地址（替换为你的后端地址）
  env: {
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1',
  },
};

export default nextConfig;
