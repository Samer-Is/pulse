/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'standalone',
  
  // Image optimization
  images: {
    domains: [
      's3.us-east-1.amazonaws.com',
      'pulse-ai-studio-prod-assets.s3.amazonaws.com',
    ],
    formats: ['image/webp', 'image/avif'],
  },
  
  // Environment variables exposed to browser
  env: {
    NEXT_PUBLIC_API_BASE: process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8080',
    NEXT_PUBLIC_GATEWAY_BASE: process.env.NEXT_PUBLIC_GATEWAY_BASE || 'http://localhost:8081',
  },
  
  // Headers for security
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
