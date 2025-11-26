'use client'

import { useState, useEffect, useMemo } from 'react'
import Image from 'next/image'
import ThumbnailRibbon from './components/ThumbnailRibbon'
import AnnotationViewer from './components/AnnotationViewer'
import PlatformBadge from './components/PlatformBadge'
import { ImageData, Annotation, PromptAnnotation, PlatformInfo } from './types'
import { Sparkles, ChevronDown, Loader2, ExternalLink, Sun, Moon } from 'lucide-react'

export default function Dashboard() {
  const [images, setImages] = useState<ImageData[]>([])
  const [selectedImageIndex, setSelectedImageIndex] = useState(0)
  const [annotations, setAnnotations] = useState<Record<string, Annotation[]>>({})
  const [platformInfo, setPlatformInfo] = useState<PlatformInfo | null>(null)
  const [selectedModel, setSelectedModel] = useState<string>('')
  const [selectedPromptKey, setSelectedPromptKey] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [imageLoading, setImageLoading] = useState(false)
  const [isDark, setIsDark] = useState(false)

  // Check initial theme
  useEffect(() => {
    setIsDark(document.documentElement.classList.contains('dark'))
  }, [])

  const toggleTheme = () => {
    const newIsDark = !isDark
    setIsDark(newIsDark)
    if (newIsDark) {
      document.documentElement.classList.add('dark')
      localStorage.theme = 'dark'
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.theme = 'light'
    }
  }

  // Load image list
  useEffect(() => {
    async function loadImageList() {
      try {
        const basePath = process.env.NEXT_PUBLIC_BASE_PATH || ''
        const response = await fetch(`${basePath}/image-list.json`)
        if (response.ok) {
          const data = await response.json()
          const imageList: ImageData[] = data.images.map((imageName: string) => ({
            id: imageName,
            thumbnailPath: `${basePath}/thumbnails/${imageName}.jpg`,
            imagePath: `${basePath}/downsampled/${imageName}.jpg`,
            annotationPath: `${basePath}/annotations/nsd/${imageName}_annotations.json`
          }))
          setImages(imageList)
        } else {
          console.error('Failed to load image list')
        }
      } catch (error) {
        console.error('Error loading image list:', error)
      } finally {
        setLoading(false)
      }
    }

    loadImageList()
  }, [])

  // Load annotations for selected image
  useEffect(() => {
    if (images.length > 0 && selectedImageIndex < images.length) {
      loadAnnotationsForImage(images[selectedImageIndex].id)
    }
  }, [selectedImageIndex, images])

  // Get available models from current image annotations
  const availableModels = useMemo(() => {
    if (!images[selectedImageIndex]) return []
    const imageAnnotations = annotations[images[selectedImageIndex].id] || []
    return Array.from(new Set(imageAnnotations.map(a => a.model)))
  }, [annotations, selectedImageIndex, images])

  // Get available prompt keys for selected model
  const availablePromptKeys = useMemo(() => {
    if (!images[selectedImageIndex] || !selectedModel) return []
    const imageAnnotations = annotations[images[selectedImageIndex].id] || []
    const modelAnnotation = imageAnnotations.find(a => a.model === selectedModel)
    if (modelAnnotation && modelAnnotation.prompts) {
      return Object.keys(modelAnnotation.prompts)
    }
    return []
  }, [annotations, selectedImageIndex, images, selectedModel])

  // Get current model annotation (includes platform override if present)
  const currentModelAnnotation = useMemo(() => {
    if (!images[selectedImageIndex] || !selectedModel) return null
    const imageAnnotations = annotations[images[selectedImageIndex].id] || []
    return imageAnnotations.find(a => a.model === selectedModel) || null
  }, [annotations, selectedImageIndex, images, selectedModel])

  // Get current prompt annotation
  const currentPromptAnnotation = useMemo(() => {
    if (!currentModelAnnotation || !selectedPromptKey) return null
    return currentModelAnnotation.prompts[selectedPromptKey] || null
  }, [currentModelAnnotation, selectedPromptKey])

  // Get effective platform (annotation override or default)
  const effectivePlatform = useMemo(() => {
    return currentModelAnnotation?.platform || platformInfo
  }, [currentModelAnnotation, platformInfo])

  async function loadAnnotationsForImage(imageId: string) {
    setImageLoading(true)
    try {
      const basePath = process.env.NEXT_PUBLIC_BASE_PATH || ''
      const response = await fetch(`${basePath}/annotations/nsd/${imageId}_annotations.json`)
      if (response.ok) {
        const data = await response.json()
        setAnnotations(prev => ({ ...prev, [imageId]: data.annotations || [] }))

        // Extract platform info from metadata if available
        if (data.metadata?.platform) {
          setPlatformInfo(data.metadata.platform)
        }

        // Auto-select first model and prompt if nothing selected
        if (data.annotations && data.annotations.length > 0) {
          const firstAnnotation = data.annotations[0]

          // Keep sticky selection or set new defaults
          const hasModel = data.annotations.some((a: Annotation) => a.model === selectedModel)
          if (!hasModel || !selectedModel) {
            setSelectedModel(firstAnnotation.model)
            const firstPromptKey = Object.keys(firstAnnotation.prompts)[0]
            setSelectedPromptKey(firstPromptKey)
          } else {
            // Check if current prompt key exists in new model
            const modelAnnotation = data.annotations.find((a: Annotation) => a.model === selectedModel)
            if (modelAnnotation && modelAnnotation.prompts) {
              const hasPromptKey = Object.keys(modelAnnotation.prompts).includes(selectedPromptKey)
              if (!hasPromptKey) {
                const firstPromptKey = Object.keys(modelAnnotation.prompts)[0]
                setSelectedPromptKey(firstPromptKey)
              }
            }
          }
        }
      }
    } catch (error) {
      console.error('Error loading annotations:', error)
    } finally {
      setImageLoading(false)
    }
  }

  const handleImageSelect = (index: number) => {
    setSelectedImageIndex(index)
  }

  // Format prompt key for display
  const formatPromptKey = (key: string) => {
    return key.split('_').map(word =>
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--bg-primary)] flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-agi-teal dark:text-agi-teal-400 animate-spin mx-auto mb-4" />
          <div className="text-xl text-agi-teal-800 dark:text-agi-teal-200">Loading annotation interface...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[var(--bg-primary)] flex flex-col">
      {/* Header */}
      <header className="glass-header">
        <div className="px-3 md:px-6 py-3 md:py-4 flex flex-col md:flex-row items-center justify-between gap-2">
          <a
            href="https://annotation.garden"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-3 md:gap-4 hover:opacity-90 transition-opacity"
          >
            <img
              src={`${process.env.NEXT_PUBLIC_BASE_PATH || ''}/AGI-square.svg`}
              alt="AGI Logo"
              className="w-10 h-10 md:w-12 md:h-12"
            />
            <div className="flex flex-col">
              <div className="flex flex-col leading-tight">
                <span className="text-base md:text-xl font-bold tracking-wide text-agi-teal dark:text-white">
                  ANNOTATION GARDEN
                </span>
                <span className="text-xs md:text-sm font-semibold tracking-widest text-stone-500 dark:text-zinc-500">
                  INITIATIVE
                </span>
              </div>
            </div>
          </a>
          <div className="flex items-center gap-4">
            <div className="flex flex-col items-center gap-1">
              <div className="flex items-center gap-2 px-4 py-2 bg-agi-teal/10 dark:bg-agi-teal/20 rounded-lg border border-agi-teal/20 dark:border-agi-teal/30">
                <Sparkles className="w-4 h-4 md:w-5 md:h-5 text-agi-orange" />
                <div className="flex flex-col">
                  <span className="text-xs text-agi-teal-500 dark:text-agi-teal-400 font-medium">Project</span>
                  <span className="text-sm md:text-base font-semibold text-agi-teal dark:text-white">Image Annotation</span>
                </div>
              </div>
              <span className="text-xs md:text-sm text-agi-teal-600 dark:text-agi-teal-400 font-medium text-center">NSD Shared 1000 Dataset</span>
            </div>
            {/* Theme toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-full text-agi-teal-600 dark:text-zinc-400 hover:bg-agi-teal/10 dark:hover:bg-white/10 transition-colors"
              aria-label="Toggle theme"
            >
              {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1 flex flex-col">
        <div className="flex-1 p-3 md:p-6 flex flex-col lg:flex-row gap-4 md:gap-6 min-h-0">
          {/* Image Viewer - Full width on mobile, constrained on desktop */}
          <div className="flex flex-col gap-4 lg:max-w-[600px] lg:min-w-[400px] w-full">
            <div className="relative glass-card rounded-2xl shadow-sm p-2 h-[50vh] md:h-full md:max-h-[600px] flex items-center justify-center">
              {imageLoading && (
                <div className="absolute inset-0 bg-white/80 dark:bg-zinc-900/80 backdrop-blur-sm z-10 flex items-center justify-center rounded-2xl">
                  <Loader2 className="w-8 h-8 text-agi-teal dark:text-agi-teal-400 animate-spin" />
                </div>
              )}
              {images[selectedImageIndex] && (
                <div className="flex items-center justify-center">
                  <img
                    src={images[selectedImageIndex].imagePath}
                    alt={`NSD Image ${selectedImageIndex + 1}`}
                    className="max-w-full max-h-[580px] object-contain rounded-lg"
                  />
                </div>
              )}
            </div>

            {/* Image Info Bar */}
            <div className="glass-card rounded-xl shadow-sm px-4 py-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <span className="text-sm text-agi-teal-600 dark:text-agi-teal-400">Image ID:</span>
                  <span className="text-sm font-mono text-agi-teal dark:text-white">
                    {images[selectedImageIndex]?.id || 'Loading...'}
                  </span>
                </div>
                <div className="text-sm text-agi-teal-600 dark:text-agi-teal-400">
                  {selectedImageIndex + 1} / {images.length}
                </div>
              </div>
            </div>
          </div>

          {/* Controls and Annotations - Full width on mobile, side panel on desktop */}
          <div className="flex-1 flex flex-col gap-4 min-w-0 w-full lg:w-auto">
            {/* Model Selection */}
            <div className="glass-card rounded-xl shadow-sm p-4">
              <label className="block text-sm font-medium text-agi-teal-700 dark:text-agi-teal-300 mb-2">
                Vision Model
              </label>
              <div className="relative">
                <select
                  value={selectedModel}
                  onChange={(e) => {
                    setSelectedModel(e.target.value)
                    // Reset prompt selection when model changes
                    setSelectedPromptKey('')
                  }}
                  className="w-full px-4 py-3 bg-stone-50 dark:bg-zinc-800 border border-agi-teal/20 dark:border-white/10 rounded-lg text-agi-teal-800 dark:text-white appearance-none focus:outline-none focus:border-agi-teal dark:focus:border-agi-teal-400 focus:ring-2 focus:ring-agi-teal/20 dark:focus:ring-agi-teal/30 transition-all"
                >
                  <option value="">Select a model</option>
                  {availableModels.map(model => (
                    <option key={model} value={model}>{model}</option>
                  ))}
                </select>
                <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-agi-teal-500 dark:text-agi-teal-400 pointer-events-none" />
              </div>
            </div>

            {/* Prompt Selection */}
            <div className="glass-card rounded-xl shadow-sm p-4">
              <label className="block text-sm font-medium text-agi-teal-700 dark:text-agi-teal-300 mb-2">
                Annotation Type
              </label>
              <div className="relative">
                <select
                  value={selectedPromptKey}
                  onChange={(e) => setSelectedPromptKey(e.target.value)}
                  className="w-full px-4 py-3 bg-stone-50 dark:bg-zinc-800 border border-agi-teal/20 dark:border-white/10 rounded-lg text-agi-teal-800 dark:text-white appearance-none focus:outline-none focus:border-agi-teal dark:focus:border-agi-teal-400 focus:ring-2 focus:ring-agi-teal/20 dark:focus:ring-agi-teal/30 transition-all"
                  disabled={!selectedModel}
                >
                  <option value="">Select annotation type</option>
                  {availablePromptKeys.map(key => (
                    <option key={key} value={key}>
                      {formatPromptKey(key)}
                    </option>
                  ))}
                </select>
                <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-agi-teal-500 dark:text-agi-teal-400 pointer-events-none" />
              </div>
            </div>

            {/* Annotation Display - Fixed height on mobile, flexible on desktop */}
            <div className="h-[40vh] lg:h-auto lg:flex-1 glass-card rounded-xl shadow-sm p-4 overflow-hidden flex flex-col">
              <h3 className="font-semibold text-agi-teal dark:text-white mb-3 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-agi-orange" />
                Annotation Details
              </h3>
              <div className="flex-1 overflow-auto">
                {currentPromptAnnotation ? (
                  <AnnotationViewer annotation={currentPromptAnnotation} platform={effectivePlatform} />
                ) : (
                  <div className="text-agi-teal-500 dark:text-zinc-500 text-center py-8">
                    {!selectedModel ? 'Select a vision model to explore annotations' :
                     !selectedPromptKey ? 'Choose an annotation type to view' :
                     'No annotations available for this selection'}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Thumbnail Ribbon */}
        <div className="px-3 md:px-6 pb-3">
          <ThumbnailRibbon
            images={images}
            selectedIndex={selectedImageIndex}
            onSelect={handleImageSelect}
          />
        </div>

        {/* Footer */}
        <footer className="glass-footer px-6 py-3">
          <div className="flex flex-col md:flex-row items-center justify-between gap-2">
            <div className="text-sm text-agi-teal-600 dark:text-zinc-400">
              © 2025{' '}
              <a
                href="https://annotation.garden"
                target="_blank"
                rel="noopener noreferrer"
                className="text-agi-teal dark:text-agi-teal-400 hover:text-agi-orange transition-colors inline-flex items-center gap-1"
              >
                Annotation Garden Initiative
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
            {platformInfo && (
              <div className="flex items-center gap-2">
                <span className="text-xs text-agi-teal-500 dark:text-zinc-500">Inference Platform:</span>
                <PlatformBadge platform={platformInfo} />
              </div>
            )}
          </div>
        </footer>
      </main>
    </div>
  )
}
