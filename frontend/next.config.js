/** @type {import('next').NextConfig} */

const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['localhost'],
    unoptimized: true,
  },
  output: 'export',
  // Served at annotation.garden/image-annotation/ by the assets-only Worker
  // in worker/ (worker/stage.sh copies out/ under image-annotation/), so the
  // generated /_next/ asset paths carry this prefix. Data and image
  // paths in the app are relative to the page, which is why trailingSlash
  // matters: "/image-annotation/" resolves "image-list.json" under the mount,
  // the bare "/image-annotation" would not (the asset handler redirects it).
  basePath: '/image-annotation',
  trailingSlash: true,
}

module.exports = nextConfig