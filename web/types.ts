
export interface EnergySplit {
  deploy_straight: number;
  deploy_corner: number;
  harvest: number;
}

export interface Rule {
  rule: string;
  condition: string;
  action: EnergySplit;
  confidence: number;
  uplift_win_pct: number;
  rationale: string;
  caveats?: string;
}

export interface Playbook {
  rules: Rule[];
  generated_at: string;
  num_simulations: number;
}

export interface DiscoveryTelemetryFrame {
  phase: string;
  progress: number;
  scenarios: number;
  message: string;
  delay_ms: number;
}

export interface DiscoveryStrategyMetric {
  codename: string;
  focus: string;
  win_share: number;
  fastest_lap_delta: number;
  battery_margin: number;
  color: string;
}

export interface DiscoveryArenaMock {
  run_id: string;
  scenarios_completed: number;
  elapsed_sec: number;
  scenarios_per_sec: number;
  energy_reclaimed_mj: number;
  peak_tyre_surface_temp: number;
  telemetry: DiscoveryTelemetryFrame[];
  strategies: DiscoveryStrategyMetric[];
}

export interface Recommendation {
  rule: string;
  action: EnergySplit;
  confidence: number;
  rationale: string;
}

export interface BoxWallResponse {
  recommendations: Recommendation[];
  latency_ms: number;
}
