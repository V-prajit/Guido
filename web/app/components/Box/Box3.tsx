import type { CSSProperties, ReactNode } from 'react';

interface BoxProps {
  className?: string;
  style?: CSSProperties;
  children?: ReactNode;
}

const baseClasses =
  'relative flex h-full w-full flex-col overflow-hidden rounded-2xl border border-border bg-bg-secondary text-text-primary shadow-lg shadow-black/20';

const defaultLayout: CSSProperties = {
  gridColumn: '4 / span 3',
  gridRow: '1 / span 3',
};

const overlayStyle: CSSProperties = {
  display: "none",
};
export default function Box3({ className, style, children }: BoxProps) {
  const composedClassName = className ? `${baseClasses} ${className}` : baseClasses;
  const mergedStyle = style ? { ...defaultLayout, ...style } : defaultLayout;

  return (
    <section className={composedClassName} style={mergedStyle}>
      <div className="pointer-events-none absolute inset-0 rounded-[inherit]" style={overlayStyle} aria-hidden />
      <div className="relative z-[1] flex flex-1 flex-col p-6">
        <h3 className="text-sm font-bold text-text-primary mb-4 tracking-wide">OPPONENT STRATEGY</h3>
        <div className="space-y-2">
          <div className="flex items-center justify-between border-b border-border/20 pb-2">
            <span className="text-sm text-text-primary">Early Pit</span>
            <span className="text-xs text-text-secondary">Verstappen</span>
          </div>
          <div className="flex items-center justify-between border-b border-border/20 pb-2">
            <span className="text-sm text-text-primary">Fuel Management</span>
            <span className="text-xs text-text-secondary">Hamilton</span>
          </div>
          <div className="flex items-center justify-between pb-2">
            <span className="text-sm text-text-primary">Tire Conservation</span>
            <span className="text-xs text-text-secondary">Leclerc</span>
          </div>
        </div>
      </div>
    </section>
  );
}
