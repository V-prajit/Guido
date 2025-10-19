export interface EnergySplit {
  deploy_straight: number;
  deploy_corner: number;
  harvest: number;
}

export interface AgentProfile {
  id: string;
  codename: string;
  strapline: string;
  color: string;
  accent: string;
  glow: string;
  position: number;
  lap_time: number;
  gap_to_leader: number;
  description: string;
  energy_split: EnergySplit;
}

export interface CircuitMeta {
  name: string;
  weekend: string;
  season: string;
  total_laps: number;
  turns: number;
  powered_by: string;
}

export interface TrackSection {
  id: string;
  label: string;
  agent_one_deploy: number;
  agent_two_deploy: number;
  svg_path: string;
}

export interface PerformanceMetric {
  label: string;
  unit?: string;
  agent_one: number;
  agent_two: number;
}

export interface LapBatteryPoint {
  lap: number;
  agent_one: number;
  agent_two: number;
}

export interface LapDeltaPoint {
  lap: number;
  delta: number;
}

export interface DiscoveryArenaData {
  circuit: CircuitMeta;
  agents: [AgentProfile, AgentProfile];
  track_sections: TrackSection[];
  metrics: PerformanceMetric[];
  lap_battery: LapBatteryPoint[];
  lap_delta: LapDeltaPoint[];
}

export type RuleDiscipline = 'energy' | 'tyre' | 'fuel' | 'aero';

export interface RuleHeatmapCell {
  lap: number;
  battery: number;
  effectiveness: number;
}

export interface RuleImpact {
  baseline: number;
  uplift: number;
  expected_outcome: string;
}

export interface StrategicRule {
  id: string;
  rule: string;
  discipline: RuleDiscipline;
  icon: string;
  condition: string;
  action: EnergySplit;
  confidence: number;
  impact: RuleImpact;
  rationale: string;
  caveats?: string;
  heatmap: RuleHeatmapCell[];
}

export interface PlaybookAnalysis {
  summary: {
    total_rules: number;
    generated_at: string;
    num_simulations: number;
  };
  rules: StrategicRule[];
}

export interface RaceState {
  lap: number;
  total_laps: number;
  position: number;
  gap_ahead: number;
  gap_behind: number;
  tyre_compound: string;
  tyre_life: number;
  battery_soc: number;
  fuel_remaining: number;
  track_condition: string;
}

export interface TelemetryGauge {
  label: string;
  value: number;
  unit?: string;
  max: number;
  color: string;
}

export interface ScenarioControls {
  rain_forecasted: boolean;
  safety_car_risk: number;
  aggression: number;
}

export interface RecommendationAction extends EnergySplit {
  fuel_mode: string;
  note?: string;
}

export interface RecommendationDetail {
  strategy: string;
  confidence: number;
  expected_outcome: string;
  rationale: string;
  action: RecommendationAction;
  alternative?: RecommendationAction & { summary: string };
}

export interface BoxWallData {
  state: RaceState;
  telemetry: TelemetryGauge[];
  controls: ScenarioControls;
  recommendation: RecommendationDetail;
  latency_ms: number;
  last_updated: string;
}
