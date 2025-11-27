/** @type {import('next').NextConfig} */

const basePath = '/image-annotation'

const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['localhost'],
    unoptimized: true,
  },
  basePath: basePath,
  assetPrefix: basePath,
  output: 'export',
  env: {
    NEXT_PUBLIC_BASE_PATH: basePath
  },
}

module.exports = nextConfig