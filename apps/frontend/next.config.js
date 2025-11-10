/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  
  // i18n (Arabic/English)
  i18n: {
    locales: ['ar', 'en'],
    defaultLocale: 'ar',
    localeDetection: true,
  },
  
  // Image optimization
  images: {
    domains: [
      's3.eu-central-1.amazonaws.com',
      'ai-studio-assets.s3.amazonaws.com',
      // Add CloudFront domain when available
    ],
    formats: ['image/webp', 'image/avif'],
  },
  
  // Environment variables exposed to browser
  env: {
    NEXT_PUBLIC_API_BASE: process.env.NEXT_PUBLIC_API_BASE,
    NEXT_PUBLIC_GATEWAY_BASE: process.env.NEXT_PUBLIC_GATEWAY_BASE,
    NEXT_PUBLIC_CDN_BASE: process.env.NEXT_PUBLIC_CDN_BASE,
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
