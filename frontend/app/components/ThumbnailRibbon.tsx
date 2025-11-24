'use client'

import { useRef, useEffect } from 'react'
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

  return (
    <div className="bg-white/80 backdrop-blur-md rounded-xl border border-agi-teal/10 shadow-sm p-2 md:p-4">
      <div className="relative flex items-center">
        {/* Left scroll button */}
        <button
          onClick={scrollLeft}
          className="absolute left-2 z-10 bg-white/90 hover:bg-agi-teal/10 backdrop-blur-sm rounded-full p-2 shadow-md border border-agi-teal/20 transition-all hover:scale-110"
          aria-label="Scroll left"
        >
          <ChevronLeft className="w-5 h-5 text-agi-teal" />
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
                    ? 'ring-2 ring-agi-teal ring-offset-2 ring-offset-transparent scale-110 shadow-xl shadow-agi-teal/20'
                    : 'hover:scale-105 hover:shadow-lg hover:shadow-agi-teal/10'
                  }
                `}
                aria-label={`Select image ${imageNumber}`}
              >
                <div className={`relative ${selectedIndex === index ? 'brightness-100' : 'brightness-90'}`}>
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
                        : 'bg-white/80 text-agi-teal-700'
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
          className="absolute right-2 z-10 bg-white/90 hover:bg-agi-teal/10 backdrop-blur-sm rounded-full p-2 shadow-md border border-agi-teal/20 transition-all hover:scale-110"
          aria-label="Scroll right"
        >
          <ChevronRight className="w-5 h-5 text-agi-teal" />
        </button>
      </div>

      {/* Progress indicator */}
      <div className="mt-3 flex items-center justify-center gap-2">
        <div className="flex gap-1">
          {Array.from({ length: Math.min(10, Math.ceil(images.length / 10)) }).map((_, i) => (
            <div
              key={i}
              className={`h-1 rounded-full transition-all ${
                Math.floor(selectedIndex / 10) === i
                  ? 'w-8 bg-gradient-to-r from-agi-teal to-agi-orange'
                  : 'w-2 bg-agi-teal/20'
              }`}
            />
          ))}
        </div>
        <span className="text-xs text-agi-teal-600 ml-2">
          {selectedIndex + 1} / {images.length}
        </span>
      </div>
    </div>
  )
}
