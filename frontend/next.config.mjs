/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/:path*',
      },
    ]
  },
  async redirects() {
    return [
      {
        source: '/chat/:path*',
        missing: [
          {
            type: 'cookie',
            key: 'jwt_token',
          },
        ],
        destination: '/login',
        permanent: false,
      },
      {
        source: '/login',
        has: [
          {
            type: 'cookie',
            key: 'jwt_token',
          },
        ],
        destination: '/chat',
        permanent: false,
      },
      {
        source: '/register',
        has: [
          {
            type: 'cookie',
            key: 'jwt_token',
          },
        ],
        destination: '/chat',
        permanent: false,
      },
    ]
  },
}

export default nextConfig
