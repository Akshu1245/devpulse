import type { NextConfig } from "next";

const backendUrl = (process.env.BACKEND_URL || 'http://localhost:8000').replace(/\/$/, '');

const nextConfig: NextConfig = {
  output: 'standalone',
  allowedDevOrigins: ['*'],
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
      {
        source: '/health',
        destination: `${backendUrl}/health`,
      },
      {
        source: '/openapi.json',
        destination: `${backendUrl}/openapi.json`,
      },
      {
        source: '/backend-docs',
        destination: `${backendUrl}/docs`,
      },
    ];
  },
};

export default nextConfig;
