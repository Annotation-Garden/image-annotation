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