import type { CSSProperties, ReactNode } from 'react';

interface BoxProps {
  className?: string;
  style?: CSSProperties;
  children?: ReactNode;
}

const baseClasses =
  'relative flex h-full w-full flex-col overflow-hidden rounded-2xl border border-border bg-bg-secondary text-text-primary shadow-lg shadow-black/20';

const defaultLayout: CSSProperties = {
  gridColumn: '10 / span 3',
  gridRow: '1 / span 5',
};

const overlayStyle: CSSProperties = {
  display: "none",
};
export default function Box7({ className, style, children }: BoxProps) {
  const composedClassName = className ? `${baseClasses} ${className}` : baseClasses;
  const mergedStyle = style ? { ...defaultLayout, ...style } : defaultLayout;

  return (
    <section className={composedClassName} style={mergedStyle}>
      <div className="pointer-events-none absolute inset-0 rounded-[inherit]" style={overlayStyle} aria-hidden />
      <div className="relative z-[1] flex flex-1 flex-col p-6">
        <h3 className="text-sm font-bold text-text-primary mb-4 tracking-wide">DECISION LOG</h3>
        <div className="space-y-2 max-h-full overflow-y-auto">
          <div className="flex items-center justify-between border-b border-border/20 pb-2">
            <div className="flex-1">
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm text-text-primary">Lap 15</span>
                <span className="text-xs text-text-secondary/40">14:23</span>
              </div>
              <p className="text-xs text-text-secondary">Deploy aggressive overtake mode</p>
            </div>
            <span className="text-text-primary ml-3">✓</span>
          </div>
          <div className="flex items-center justify-between border-b border-border/20 pb-2">
            <div className="flex-1">
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm text-text-primary">Lap 12</span>
                <span className="text-xs text-text-secondary/40">14:18</span>
              </div>
              <p className="text-xs text-text-secondary">Pit stop for soft compound tires</p>
            </div>
            <span className="text-text-primary ml-3">✗</span>
          </div>
          <div className="flex items-center justify-between border-b border-border/20 pb-2">
            <div className="flex-1">
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm text-text-primary">Lap 8</span>
                <span className="text-xs text-text-secondary/40">14:12</span>
              </div>
              <p className="text-xs text-text-secondary">Maintain pace, conserve battery</p>
            </div>
            <span className="text-text-primary ml-3">✓</span>
          </div>
          <div className="flex items-center justify-between pb-2">
            <div className="flex-1">
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm text-text-primary">Lap 5</span>
                <span className="text-xs text-text-secondary/40">14:07</span>
              </div>
              <p className="text-xs text-text-secondary">Increase fuel mix to mode 3</p>
            </div>
            <span className="text-text-primary ml-3">✓</span>
          </div>
        </div>
      </div>
    </section>
  );
}
