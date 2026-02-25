export interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  agent: string;
}

export interface AgentResponse {
  agent: string;
  status: 'success' | 'error' | 'pending';
  content: string;
  metadata?: Record<string, unknown>;
}

export interface Product {
  name: string;
  price?: string;
  commission?: string;
  rating?: number;
  url?: string;
  affiliate_network?: string;
  reason?: string;
}

export interface EarningsProjection {
  conservative: string;
  viral: string;
}

export interface ScriptColumn {
  timecode: string;
  visual_cue: string;
  audio: string;
}

export interface ScriptData {
  script_columns: ScriptColumn[];
  raw_content?: string;
  topic?: string;
  language?: string;
  seo_keywords?: string[];
  script_source?: 'baidu' | 'ollama' | 'template';
}

export interface GenerationResult {
  topic: string;
  script: string;
  variations: string[];
  captions: string[];
  video_path?: string;
  monetization_brief: string;
  products: Product[];
  earnings_projection: EarningsProjection;
  status: 'completed' | 'in_progress' | 'failed';
}

export interface GenerationStatus {
  generation_id?: string;
  topic?: string;
  language?: string;
  status: 'idle' | 'running' | 'script_ready' | 'completed' | 'failed';
  progress: number;
  phase?: string;
  error?: string;
  result?: GenerationResult;
  script_data?: ScriptData;
  variations?: any[];
}

export interface PipelineStatus {
  agent_alpha: { status: 'idle' | 'running' | 'completed' | 'failed'; message?: string };
  agent_beta: { status: 'idle' | 'running' | 'completed' | 'failed'; message?: string };
  agent_gamma: { status: 'idle' | 'running' | 'completed' | 'failed'; message?: string };
  agent_delta: { status: 'idle' | 'running' | 'completed' | 'failed'; message?: string };
}
