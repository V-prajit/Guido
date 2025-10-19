import type { CSSProperties, ReactNode } from 'react';

interface BoxProps {
  className?: string;
  style?: CSSProperties;
  children?: ReactNode;
}

const baseClasses =
  'relative flex h-full w-full flex-col overflow-hidden rounded-2xl border border-border bg-bg-secondary text-text-primary shadow-lg shadow-black/20';

const defaultLayout: CSSProperties = {
  gridColumn: '7 / span 3',
  gridRow: '1 / span 3',
};

const overlayStyle: CSSProperties = {
  display: "none",
};
export default function Box6({ className, style, children }: BoxProps) {
  const composedClassName = className ? `${baseClasses} ${className}` : baseClasses;
  const mergedStyle = style ? { ...defaultLayout, ...style } : defaultLayout;

  return (
    <section className={composedClassName} style={mergedStyle}>
      <div className="pointer-events-none absolute inset-0 rounded-[inherit]" style={overlayStyle} aria-hidden />
      <div className="relative z-[1] flex flex-1 flex-col p-6">
        <h3 className="text-sm font-bold text-text-primary mb-4 tracking-wide">AGENT PERFORMANCE</h3>
        <div className="space-y-3">
          <div className="border-b border-border/20 pb-2">
            <div className="flex justify-between items-center mb-1">
              <span className="text-sm font-bold text-text-primary">You</span>
              <span className="text-xs text-text-secondary">65% optimal</span>
            </div>
          </div>
          <div className="border-b border-border/20 pb-2">
            <div className="flex justify-between items-center mb-1">
              <span className="text-sm text-text-primary">Pure AI</span>
              <span className="text-xs text-text-secondary">98% optimal</span>
            </div>
          </div>
          <div className="border-b border-border/20 pb-2">
            <div className="flex justify-between items-center mb-1">
              <span className="text-sm text-text-primary">Verstappen</span>
              <span className="text-xs text-text-secondary">72% optimal</span>
            </div>
          </div>
          <div className="pb-2">
            <div className="flex justify-between items-center mb-1">
              <span className="text-sm text-text-primary">Hamilton</span>
              <span className="text-xs text-text-secondary">68% optimal</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
