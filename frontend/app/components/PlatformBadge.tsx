'use client'

import { PlatformInfo } from '../types'
import { Cpu, Monitor } from 'lucide-react'

interface PlatformBadgeProps {
  platform?: PlatformInfo | null
}

// Map vendor to display color
const vendorColors: Record<string, string> = {
  nvidia: 'text-green-600 dark:text-green-400',
  amd: 'text-red-600 dark:text-red-400',
  intel: 'text-blue-600 dark:text-blue-400',
  apple: 'text-gray-600 dark:text-gray-400',
}

// Map compute backend to display name
const backendNames: Record<string, string> = {
  cuda: 'CUDA',
  rocm: 'ROCm',
  mps: 'Metal',
  oneapi: 'oneAPI',
  cpu: 'CPU',
}

export default function PlatformBadge({ platform }: PlatformBadgeProps) {
  if (!platform) {
    return null
  }

  const hasGPU = platform.accelerators && platform.accelerators.length > 0
  const primaryGPU = hasGPU ? platform.accelerators[0] : null
  const backendDisplay = platform.compute_backend
    ? backendNames[platform.compute_backend] || platform.compute_backend.toUpperCase()
    : null

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 bg-agi-teal/5 dark:bg-agi-teal/10 rounded-lg border border-agi-teal/10 dark:border-agi-teal/20">
      {hasGPU ? (
        <Monitor className="w-4 h-4 text-agi-orange" />
      ) : (
        <Cpu className="w-4 h-4 text-agi-teal-500" />
      )}
      <div className="flex items-center gap-2 text-xs">
        {primaryGPU ? (
          <>
            <span className={`font-medium ${vendorColors[primaryGPU.vendor] || 'text-agi-teal-600'}`}>
              {primaryGPU.name}
            </span>
            {primaryGPU.memory_mb && (
              <span className="text-agi-teal-500 dark:text-zinc-500">
                ({Math.round(primaryGPU.memory_mb / 1024)}GB)
              </span>
            )}
          </>
        ) : (
          <span className="text-agi-teal-600 dark:text-zinc-400">CPU Only</span>
        )}
        {backendDisplay && (
          <span className="text-agi-teal-400 dark:text-zinc-500">
            • {backendDisplay}
          </span>
        )}
      </div>
    </div>
  )
}
