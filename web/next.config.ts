import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Disable React Strict Mode to prevent WebSocket double-connection issues
  reactStrictMode: false,
};

export default nextConfig;
