'use client'

import { useRef, useEffect, useState, useCallback } from 'react'
import { ImageData } from '../types'
import { ChevronLeft, ChevronRight } from 'lucide-react'

interface ThumbnailRibbonProps {
  images: ImageData[]
  selectedIndex: number
  onSelect: (index: number) => void
}

export default function ThumbnailRibbon({ images, selectedIndex, onSelect }: ThumbnailRibbonProps) {
  const scrollContainerRef = useRef<HTMLDivElement>(null)
  const thumbnailRefs = useRef<(HTMLButtonElement | null)[]>([])
  const progressBarRef = useRef<HTMLDivElement>(null)
  const [isDragging, setIsDragging] = useState(false)

  // Scroll to selected thumbnail when it changes
  useEffect(() => {
    if (thumbnailRefs.current[selectedIndex] && scrollContainerRef.current) {
      const thumbnail = thumbnailRefs.current[selectedIndex]
      const container = scrollContainerRef.current

      if (thumbnail) {
        const containerWidth = container.clientWidth
        const scrollLeft = thumbnail.offsetLeft - containerWidth / 2 + thumbnail.clientWidth / 2

        container.scrollTo({
          left: scrollLeft,
          behavior: 'smooth'
        })
      }
    }
  }, [selectedIndex])

  const scrollLeft = () => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollBy({
        left: -300,
        behavior: 'smooth'
      })
    }
  }

  const scrollRight = () => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollBy({
        left: 300,
        behavior: 'smooth'
      })
    }
  }

  const handleKeyNavigation = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowLeft' && selectedIndex > 0) {
      onSelect(selectedIndex - 1)
    } else if (e.key === 'ArrowRight' && selectedIndex < images.length - 1) {
      onSelect(selectedIndex + 1)
    }
  }

  // Handle click/drag on progress bar to jump to position
  const handleProgressInteraction = useCallback((clientX: number) => {
    if (!progressBarRef.current || images.length === 0) return

    const rect = progressBarRef.current.getBoundingClientRect()
    const relativeX = Math.max(0, Math.min(clientX - rect.left, rect.width))
    const percentage = relativeX / rect.width
    const newIndex = Math.min(
      Math.floor(percentage * images.length),
      images.length - 1
    )
    onSelect(newIndex)
  }, [images.length, onSelect])

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true)
    handleProgressInteraction(e.clientX)
  }

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (isDragging) {
      handleProgressInteraction(e.clientX)
    }
  }, [isDragging, handleProgressInteraction])

  const handleMouseUp = useCallback(() => {
    setIsDragging(false)
  }, [])

  // Add/remove mouse event listeners for drag
  useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove)
      window.addEventListener('mouseup', handleMouseUp)
    }
    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isDragging, handleMouseMove, handleMouseUp])

  return (
    <div className="glass-card rounded-xl shadow-sm p-2 md:p-4">
      <div className="relative flex items-center">
        {/* Left scroll button */}
        <button
          onClick={scrollLeft}
          className="absolute left-2 z-10 bg-white/90 dark:bg-zinc-800/90 hover:bg-agi-teal/10 dark:hover:bg-agi-teal/20 backdrop-blur-sm rounded-full p-2 shadow-md border border-agi-teal/20 dark:border-white/10 transition-all hover:scale-110"
          aria-label="Scroll left"
        >
          <ChevronLeft className="w-5 h-5 text-agi-teal dark:text-agi-teal-400" />
        </button>

        {/* Thumbnail container */}
        <div
          ref={scrollContainerRef}
          className="flex gap-3 overflow-x-auto scrollbar-thin px-14 py-2"
          onKeyDown={handleKeyNavigation}
          tabIndex={0}
          style={{
            scrollbarWidth: 'thin',
            scrollbarColor: 'rgba(24, 74, 61, 0.3) transparent'
          }}
        >
          {images.map((image, index) => {
            // Extract the image number for display
            const imageNumber = image.id.match(/shared(\d+)/)?.[1] || String(index + 1)

            return (
              <button
                key={image.id}
                ref={el => {
                  thumbnailRefs.current[index] = el
                }}
                onClick={() => onSelect(index)}
                className={`
                  relative flex-shrink-0 rounded-lg overflow-hidden
                  transition-all duration-300 transform
                  ${selectedIndex === index
                    ? 'ring-2 ring-agi-teal dark:ring-agi-teal-400 ring-offset-2 ring-offset-transparent scale-110 shadow-xl shadow-agi-teal/20'
                    : 'hover:scale-105 hover:shadow-lg hover:shadow-agi-teal/10 dark:hover:shadow-agi-teal/5'
                  }
                `}
                aria-label={`Select image ${imageNumber}`}
              >
                <div className={`relative ${selectedIndex === index ? 'brightness-100' : 'brightness-90 dark:brightness-75'}`}>
                  <img
                    src={image.thumbnailPath}
                    alt={`Thumbnail ${imageNumber}`}
                    className="w-20 h-20 md:w-28 md:h-28 object-cover"
                    loading="lazy"
                  />
                  {/* Gradient overlay */}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent" />

                  {/* Image number badge */}
                  <div className={`absolute bottom-1 left-1 right-1 flex items-center justify-center`}>
                    <span className={`
                      px-2 py-0.5 rounded-full text-xs font-medium
                      ${selectedIndex === index
                        ? 'bg-agi-teal text-white'
                        : 'bg-white/80 dark:bg-zinc-800/80 text-agi-teal-700 dark:text-white'
                      }
                      backdrop-blur-sm
                    `}>
                      {imageNumber}
                    </span>
                  </div>
                </div>
              </button>
            )
          })}
        </div>

        {/* Right scroll button */}
        <button
          onClick={scrollRight}
          className="absolute right-2 z-10 bg-white/90 dark:bg-zinc-800/90 hover:bg-agi-teal/10 dark:hover:bg-agi-teal/20 backdrop-blur-sm rounded-full p-2 shadow-md border border-agi-teal/20 dark:border-white/10 transition-all hover:scale-110"
          aria-label="Scroll right"
        >
          <ChevronRight className="w-5 h-5 text-agi-teal dark:text-agi-teal-400" />
        </button>
      </div>

      {/* Progress indicator - clickable/draggable slider */}
      <div className="mt-3 flex items-center justify-center gap-3">
        <div
          ref={progressBarRef}
          className={`relative w-64 md:w-96 h-6 flex items-center cursor-pointer group ${isDragging ? 'cursor-grabbing' : 'cursor-grab'}`}
          onMouseDown={handleMouseDown}
          role="slider"
          aria-label="Image position"
          aria-valuemin={1}
          aria-valuemax={images.length}
          aria-valuenow={selectedIndex + 1}
          tabIndex={0}
        >
          {/* Track background */}
          <div className="absolute inset-x-0 h-2 bg-agi-teal/10 dark:bg-white/10 rounded-full" />

          {/* Filled track */}
          <div
            className="absolute left-0 h-2 bg-gradient-to-r from-agi-teal to-agi-orange rounded-full transition-all duration-75"
            style={{ width: `${((selectedIndex + 1) / images.length) * 100}%` }}
          />

          {/* Thumb/handle */}
          <div
            className={`absolute w-4 h-4 bg-white dark:bg-zinc-200 border-2 border-agi-teal dark:border-agi-teal-400 rounded-full shadow-md transform -translate-x-1/2 transition-transform ${
              isDragging ? 'scale-125' : 'group-hover:scale-110'
            }`}
            style={{ left: `${((selectedIndex + 1) / images.length) * 100}%` }}
          />

          {/* Segment markers */}
          <div className="absolute inset-x-0 flex justify-between px-0.5">
            {Array.from({ length: 11 }).map((_, i) => (
              <div
                key={i}
                className="w-0.5 h-1 bg-agi-teal/30 dark:bg-white/20 rounded-full"
              />
            ))}
          </div>
        </div>

        <span className="text-xs text-agi-teal-600 dark:text-agi-teal-400 font-medium min-w-[60px]">
          {selectedIndex + 1} / {images.length}
        </span>
      </div>
    </div>
  )
}
