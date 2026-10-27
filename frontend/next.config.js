/** @type {import('next').NextConfig} */

const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['localhost'],
    unoptimized: true,
  },
  output: 'export',
  // Served at annotation.garden/image-annotation/ by the Worker in worker/,
  // so the generated /_next/ asset paths carry this prefix. Data and image
  // paths in the app are relative to the page, which is why trailingSlash
  // matters: "/image-annotation/" resolves "image-list.json" under the mount,
  // the bare "/image-annotation" would not (the Worker redirects it).
  basePath: '/image-annotation',
  trailingSlash: true,
}

module.exports = nextConfig