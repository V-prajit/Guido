import type { CSSProperties, ReactNode } from 'react';

interface BoxProps {
  className?: string;
  style?: CSSProperties;
  children?: ReactNode;
}

const baseClasses =
  'relative flex h-full w-full flex-col overflow-hidden rounded-2xl border border-border bg-bg-secondary text-text-primary shadow-lg shadow-black/20';

const defaultLayout: CSSProperties = {
  gridColumn: '4 / span 9',
  gridRow: '9 / span 4',
};

const overlayStyle: CSSProperties = {
  display: "none",
};
export default function Box5({ className, style, children }: BoxProps) {
  const composedClassName = className ? `${baseClasses} ${className}` : baseClasses;
  const mergedStyle = style ? { ...defaultLayout, ...style } : defaultLayout;

  return (
    <section className={composedClassName} style={mergedStyle}>
      <div className="pointer-events-none absolute inset-0 rounded-[inherit]" style={overlayStyle} aria-hidden />
      {children ? (
        <div className="relative z-[1] flex flex-1 flex-col p-6">{children}</div>
      ) : (
        <span className="relative z-[1] p-6 text-xs font-semibold uppercase tracking-wider text-text-secondary">
          Box 5
        </span>
      )}
    </section>
  );
}
