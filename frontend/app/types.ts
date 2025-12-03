export interface ImageData {
  id: string
  thumbnailPath: string
  imagePath: string
  annotationPath: string
}

export interface PromptAnnotation {
  prompt_text: string
  response: string
  response_format: string
  response_data?: any
  error?: string | null
  hed_annotation?: string  // HED annotation for this description (from HED-bot)
  token_metrics?: {
    input_tokens: number
    output_tokens: number
    total_tokens: number
  }
  performance_metrics?: {
    total_duration_ms: number
    prompt_eval_duration_ms: number
    generation_duration_ms: number
    load_duration_ms: number
    tokens_per_second: number
  }
}

export interface Annotation {
  model: string
  temperature?: number
  prompts: Record<string, PromptAnnotation>
  platform?: PlatformInfo | null  // Override for this annotation (e.g., cloud API)
}

export interface GPUInfo {
  name: string
  vendor: string  // nvidia, amd, intel, apple
  memory_mb?: number | null
  driver_version?: string | null
}

export interface PlatformInfo {
  os_name: string
  os_version: string
  python_version: string
  accelerators: GPUInfo[]
  compute_backend?: string | null  // cuda, rocm, mps, oneapi, cpu
}

export interface AnnotationFile {
  image_id: string
  image_path: string
  annotations: Annotation[]
  metadata?: {
    processed_at?: string
    platform?: PlatformInfo
    [key: string]: any
  }
}

export interface HumanHedEntry {
  hed_short: string
  hed_long: string
  coco_id: string
  nsd_id: string
}

export type HumanHedData = Record<string, HumanHedEntry>