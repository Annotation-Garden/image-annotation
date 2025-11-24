'use client'

import { useState } from 'react'
import { PromptAnnotation } from '../types'
import { Copy, Check, FileText, FileJson, Activity, Zap } from 'lucide-react'

interface AnnotationViewerProps {
  annotation: PromptAnnotation
}

export default function AnnotationViewer({ annotation }: AnnotationViewerProps) {
  const [copied, setCopied] = useState(false)
  const [viewMode, setViewMode] = useState<'text' | 'json'>('text')

  const handleCopy = () => {
    const textToCopy = viewMode === 'json'
      ? JSON.stringify(annotation.response_data || annotation.response, null, 2)
      : annotation.response

    navigator.clipboard.writeText(textToCopy)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  // Check if we have structured JSON data
  const hasJsonData = annotation.response_data && Object.keys(annotation.response_data).length > 0

  // Render JSON data in a structured way
  const renderJsonData = (data: any) => {
    if (!data) return null

    // If it's an array of items
    if (Array.isArray(data)) {
      return (
        <div className="space-y-3">
          {data.map((item, index) => (
            <div key={index} className="bg-agi-teal/5 rounded-lg p-3 border border-agi-teal/10">
              <div className="text-xs text-agi-orange mb-2">Item {index + 1}</div>
              {renderJsonData(item)}
            </div>
          ))}
        </div>
      )
    }

    // If it's an object with properties
    if (typeof data === 'object') {
      return (
        <div className="space-y-2">
          {Object.entries(data).map(([key, value]) => (
            <div key={key} className="flex flex-col gap-1">
              <span className="text-xs text-agi-teal font-medium">
                {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:
              </span>
              {typeof value === 'object' ? (
                <div className="ml-3 border-l-2 border-agi-teal/20 pl-3">
                  {renderJsonData(value)}
                </div>
              ) : (
                <span className="text-sm text-agi-teal-800 ml-3">
                  {String(value)}
                </span>
              )}
            </div>
          ))}
        </div>
      )
    }

    // Primitive value
    return <span className="text-sm text-agi-teal-800">{String(data)}</span>
  }

  return (
    <div className="space-y-4">
      {/* Prompt Text */}
      <div className="bg-agi-teal/5 rounded-lg p-3 border border-agi-teal/10">
        <div className="text-xs text-agi-orange mb-1">Prompt</div>
        <div className="text-sm text-agi-teal-800 leading-relaxed">
          {annotation.prompt_text}
        </div>
      </div>

      {/* View mode toggle */}
      {hasJsonData && (
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode('text')}
            className={`px-3 py-1.5 rounded-lg text-sm flex items-center gap-1.5 transition-all ${
              viewMode === 'text'
                ? 'bg-agi-teal/10 text-agi-teal border border-agi-teal/30'
                : 'bg-stone-100 text-agi-teal-600 hover:bg-stone-200 border border-stone-200'
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            Text
          </button>
          <button
            onClick={() => setViewMode('json')}
            className={`px-3 py-1.5 rounded-lg text-sm flex items-center gap-1.5 transition-all ${
              viewMode === 'json'
                ? 'bg-agi-teal/10 text-agi-teal border border-agi-teal/30'
                : 'bg-stone-100 text-agi-teal-600 hover:bg-stone-200 border border-stone-200'
            }`}
          >
            <FileJson className="w-3.5 h-3.5" />
            Structured
          </button>
        </div>
      )}

      {/* Content area */}
      <div className="relative">
        <button
          onClick={handleCopy}
          className="absolute top-2 right-2 p-2 rounded-lg bg-stone-100 hover:bg-agi-teal/10 transition-all z-10"
          aria-label="Copy to clipboard"
        >
          {copied ? (
            <Check className="w-4 h-4 text-green-600" />
          ) : (
            <Copy className="w-4 h-4 text-agi-teal-600" />
          )}
        </button>

        <div className="bg-agi-teal/5 rounded-lg p-4 pr-12 max-h-[400px] overflow-y-auto border border-agi-teal/10">
          {viewMode === 'text' ? (
            <div className="whitespace-pre-wrap text-sm text-agi-teal-800 leading-relaxed">
              {annotation.response}
            </div>
          ) : hasJsonData ? (
            <div className="text-sm">
              {renderJsonData(annotation.response_data)}
            </div>
          ) : (
            <pre className="text-xs overflow-x-auto text-agi-teal-800">
              <code>{JSON.stringify(annotation.response, null, 2)}</code>
            </pre>
          )}
        </div>
      </div>

      {/* Metrics */}
      {(annotation.token_metrics || annotation.performance_metrics) && (
        <div className="grid grid-cols-2 gap-3">
          {annotation.token_metrics && (
            <div className="bg-agi-teal/5 rounded-lg p-3 border border-agi-teal/10">
              <div className="flex items-center gap-2 mb-2">
                <Activity className="w-4 h-4 text-agi-orange" />
                <span className="text-xs font-medium text-agi-teal-600">Token Usage</span>
              </div>
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-agi-teal-500">Input:</span>
                  <span className="text-agi-teal-800">{annotation.token_metrics.input_tokens}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-agi-teal-500">Output:</span>
                  <span className="text-agi-teal-800">{annotation.token_metrics.output_tokens}</span>
                </div>
                <div className="flex justify-between text-xs font-medium">
                  <span className="text-agi-teal-500">Total:</span>
                  <span className="text-agi-teal">{annotation.token_metrics.total_tokens}</span>
                </div>
              </div>
            </div>
          )}

          {annotation.performance_metrics && (
            <div className="bg-agi-teal/5 rounded-lg p-3 border border-agi-teal/10">
              <div className="flex items-center gap-2 mb-2">
                <Zap className="w-4 h-4 text-agi-orange" />
                <span className="text-xs font-medium text-agi-teal-600">Performance</span>
              </div>
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-agi-teal-500">Speed:</span>
                  <span className="text-agi-teal-800">
                    {annotation.performance_metrics.tokens_per_second.toFixed(1)} t/s
                  </span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-agi-teal-500">Time:</span>
                  <span className="text-agi-teal-800">
                    {(annotation.performance_metrics.total_duration_ms / 1000).toFixed(2)}s
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
