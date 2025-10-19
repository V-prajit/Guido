import type { CSSProperties, ReactNode } from 'react';

interface BoxProps {
  className?: string;
  style?: CSSProperties;
  children?: ReactNode;
}

const baseClasses =
  'relative flex h-full w-full flex-col overflow-hidden rounded-2xl border border-border bg-bg-secondary text-text-primary shadow-lg shadow-black/20';

const defaultLayout: CSSProperties = {
  gridColumn: '1 / span 3',
  gridRow: '9 / span 4',
};

const overlayStyle: CSSProperties = {
  display: "none",
};
export default function Box2({ className, style, children }: BoxProps) {
  const composedClassName = className ? `${baseClasses} ${className}` : baseClasses;
  const mergedStyle = style ? { ...defaultLayout, ...style } : defaultLayout;

  return (
    <section className={composedClassName} style={mergedStyle}>
      <div className="pointer-events-none absolute inset-0 rounded-[inherit]" style={overlayStyle} aria-hidden />
      <div className="relative z-[1] flex flex-1 flex-col p-6">
        <h3 className="text-sm font-bold text-text-primary mb-4 tracking-wide">SIMULATION PROGRESS</h3>
        <div className="space-y-3">
          <p className="text-2xl font-bold text-text-primary">80/100</p>
          <div className="w-full h-2 bg-text-primary/20 rounded-full overflow-hidden">
            <div className="h-full bg-text-primary w-4/5 transition-all duration-300"></div>
          </div>
          <p className="text-xs text-text-secondary">Est: 2m 15s</p>
        </div>
      </div>
    </section>
  );
}
