
export interface Rule {
  rule: string;
  condition: string;
  action: {
    deploy_straight: number;
    deploy_corner: number;
    harvest: number;
  };
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
