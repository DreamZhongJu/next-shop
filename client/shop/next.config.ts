import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  dynamicParams: true,
  allowedDevOrigins: ['http://localhost:3000', 'http://192.168.1.15:3000'],

};

export default nextConfig;
