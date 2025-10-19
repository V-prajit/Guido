import mockData from '../../mock/playbookView.json';
import type { PlaybookAnalysis } from '../../types';
import Button from '../shared/Button';
import RuleCard from './RuleCard';

const data = mockData as PlaybookAnalysis;

export default function PlaybookView() {
  return (
    <section className="flex flex-col gap-8">
      <header className="flex flex-col gap-2">
        <div className="text-[11px] font-semibold uppercase tracking-[0.38em] text-[#777]">
          Strategic Playbook · Synthesised from {data.summary.num_simulations.toLocaleString()} races
        </div>
        <h2 className="text-4xl font-black uppercase leading-tight tracking-[0.08em] text-white">
          Gemini-Curated Strategic Intelligence
        </h2>
        <div className="flex flex-wrap items-center gap-3 text-xs uppercase tracking-[0.3em] text-[#555]">
          <span>Total rules · {data.summary.total_rules}</span>
          <span>Generated at · {new Date(data.summary.generated_at).toLocaleString()}</span>
        </div>
      </header>

      <div className="grid gap-4 rounded-3xl border border-[#1f1f1f] bg-[#0B0B0B] px-6 py-5 md:flex md:items-center md:justify-between">
        <p className="max-w-2xl text-sm text-[#9f9f9f]">
          Each rule blends simulation telemetry with Gemini reasoning to capture energy deployment,
          tyre conditioning, and fuel strategy moves that convert to delta. Confidence gradients show
          when the strategy wins.
        </p>
        <div className="flex flex-wrap items-center gap-3">
          <Button>Validate on New Scenarios</Button>
          <Button variant="secondary">Export Playbook</Button>
          <Button variant="ghost">Run Ablation</Button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {data.rules.map((rule) => (
          <RuleCard key={rule.id} rule={rule} />
        ))}
      </div>
    </section>
  );
}
