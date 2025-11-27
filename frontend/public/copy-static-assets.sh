#!/bin/bash
# Copy static assets from parent directories to public folder for build

set -e

echo "Copying static assets..."

# Create directories
mkdir -p public/thumbnails public/downsampled public/annotations/nsd

# Copy thumbnails
cp -r ../data/thumbnails/* public/thumbnails/ 2>/dev/null || echo "No thumbnails to copy"

# Copy downsampled images
cp -r ../images/downsampled/* public/downsampled/ 2>/dev/null || echo "No images to copy"

# Copy annotations
cp -r ../annotations/nsd/*.json public/annotations/nsd/ 2>/dev/null || echo "No annotations to copy"

# Copy image list if it exists
cp ../data/image-list.json public/ 2>/dev/null || echo "No image-list.json to copy"

echo "Assets copied successfully"
ls -la public/
