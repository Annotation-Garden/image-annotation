# The Annotation Garden Project - Frontend

A modern AI-powered dashboard for browsing and analyzing NSD (Natural Scene Dataset) images with multiple vision model annotations.

## 🚀 Quick Start

```bash
# 1. Install dependencies
pnpm install

# 2. Copy static assets (images & annotations)
pnpm run copy-assets

# 3. Start development server
pnpm run dev
```

Visit http://localhost:3000 to see the dashboard.

## Deployment

### Building for Production

```bash
# Build and export static site
pnpm run build:static

# This will:
# 1. Copy all required assets to public/
# 2. Build the Next.js app
# 3. Export as static HTML to out/
```

The site is deployed to Cloudflare Pages automatically via GitHub Actions.

## Available Scripts

- `pnpm run dev` - Start development server
- `pnpm run build` - Build for production
- `pnpm run build:static` - Build static site with assets
- `pnpm run copy-assets` - Copy images and annotations to public folder
- `pnpm run clean` - Clean build artifacts and copied assets

## 📁 Project Structure

```
frontend/
├── app/                    # Next.js app directory
│   ├── components/        # React components
│   │   ├── ThumbnailRibbon.tsx
│   │   └── AnnotationViewer.tsx
│   ├── api/              # API routes for data fetching
│   ├── page.tsx          # Main dashboard page
│   └── layout.tsx        # Root layout
├── public/               # Static assets
│   ├── copy-static-assets.sh  # Asset copying script
│   ├── thumbnails/       # (copied) Image thumbnails
│   ├── downsampled/      # (copied) Downsampled images
│   └── annotations/      # (copied) JSON annotations
└── out/                  # Static export output
```

## 🎨 Features

- **Modern UI**: Dark theme with purple gradients and glassmorphism effects
- **Multi-Model Support**: Browse annotations from different AI vision models
- **Dynamic Analysis Types**: Multiple prompt types per model
- **Structured Data View**: Toggle between text and JSON views
- **Performance Metrics**: View token usage and processing times
- **Responsive Design**: Optimized layout for different screen sizes
- **Keyboard Navigation**: Arrow keys to navigate images

## 🔧 Configuration

The dashboard expects the following structure in the parent directory:

```
image-annotation/
├── images/
│   └── downsampled/      # Downsampled NSD images
├── data/
│   └── thumbnails/       # Generated thumbnails
└── annotations/
    └── nsd/              # JSON annotation files
```

## 📝 Asset Preparation

Before deploying, ensure you have:

1. **Downsampled images** in `../images/downsampled/`
2. **Thumbnails** in `../data/thumbnails/`
3. **Annotations** in `../annotations/nsd/`

Run `pnpm run copy-assets` to copy these to the public folder.

## 🚢 GitHub Actions Deployment

The project includes automated deployment via GitHub Actions. On push to main branch:

1. Assets are automatically copied
2. Site is built as static HTML
3. Deployed to GitHub Pages

See `.github/workflows/deploy.yml` for details.

## 📄 License

© 2025 Seyed Yahya Shirazi, Swartz Center for Computational Neuroscience, UC San Diego