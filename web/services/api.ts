/**
 * API Service Layer
 *
 * HTTP client for Strategy Gym 2026 backend endpoints.
 * All functions are typed and handle errors gracefully.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface RunRequest {
  num_scenarios: number;
  num_agents?: number;
  repeats?: number;
}

export interface RunResponse {
  run_id: string;
  scenarios_completed: number;
  csv_path: string;
  elapsed_sec: number;
}

export interface AnalyzeResponse {
  stats: Record<string, any>;
  playbook_preview: {
    num_rules: number;
    cached?: boolean;
  };
}

export interface RecommendRequest {
  lap: number;
  battery_soc: number;
  position: number;
  rain?: boolean;
  tire_age?: number;
  tire_life?: number;
  fuel_remaining?: number;
  boost_used?: number;
}

export interface RecommendResponse {
  recommendations: any[];
  latency_ms: number;
  timestamp: number;
  seed: number;
  conditions_evaluated: any[];
}

export interface HealthResponse {
  status: string;
  playbook_exists: boolean;
  latest_run: string | null;
  num_runs: number;
  max_workers: number;
}

export interface PerformanceMetrics {
  simulation_speed: number;
  recommendation_latency: number;
  adaptive_win_rate: number;
  [key: string]: any;
}

/**
 * Health check - verify backend is running
 */
export async function checkHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE_URL}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
  return res.json();
}

/**
 * Run simulation with specified scenarios
 */
export async function runSimulation(request: RunRequest): Promise<RunResponse> {
  const res = await fetch(`${API_BASE_URL}/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ message: res.statusText }));
    throw new Error(error.message || 'Simulation failed');
  }

  return res.json();
}

/**
 * Analyze latest run and generate playbook
 */
export async function analyzeRuns(): Promise<AnalyzeResponse> {
  const res = await fetch(`${API_BASE_URL}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ message: res.statusText }));
    throw new Error(error.message || 'Analysis failed');
  }

  return res.json();
}

/**
 * Get cached playbook
 */
export async function getPlaybook(): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/playbook`);

  if (!res.ok) {
    if (res.status === 404) {
      throw new Error('No playbook generated yet. Run simulation first.');
    }
    throw new Error(`Failed to fetch playbook: ${res.statusText}`);
  }

  return res.json();
}

/**
 * Get strategy recommendation for current race state
 */
export async function getRecommendation(request: RecommendRequest): Promise<RecommendResponse> {
  const res = await fetch(`${API_BASE_URL}/recommend`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ message: res.statusText }));
    throw new Error(error.message || 'Recommendation failed');
  }

  return res.json();
}

/**
 * Run validation scenarios
 */
export async function runValidation(): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/validate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ message: res.statusText }));
    throw new Error(error.message || 'Validation failed');
  }

  return res.json();
}

/**
 * Get performance metrics
 */
export async function getPerformanceMetrics(): Promise<PerformanceMetrics> {
  const res = await fetch(`${API_BASE_URL}/perf`);

  if (!res.ok) throw new Error(`Failed to fetch performance: ${res.statusText}`);

  return res.json();
}

/**
 * Run benchmark
 */
export async function runBenchmark(num_scenarios: number = 1000): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/benchmark?num_scenarios=${num_scenarios}`, {
    method: 'POST',
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ message: res.statusText }));
    throw new Error(error.message || 'Benchmark failed');
  }

  return res.json();
}

/**
 * Get run logs with pagination
 */
export async function getLogs(offset: number = 0, limit: number = 50): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/logs?offset=${offset}&limit=${limit}`);

  if (!res.ok) throw new Error(`Failed to fetch logs: ${res.statusText}`);

  return res.json();
}

/**
 * Get detailed log for specific run
 */
export async function getLogDetail(logId: string): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/logs/${logId}`);

  if (!res.ok) {
    if (res.status === 404) {
      throw new Error('Log not found');
    }
    throw new Error(`Failed to fetch log: ${res.statusText}`);
  }

  return res.json();
}
