import type { CSSProperties, ReactNode } from 'react';

interface BoxProps {
  className?: string;
  style?: CSSProperties;
  children?: ReactNode;
}

const baseClasses =
  'relative flex h-full w-full flex-col overflow-hidden rounded-3xl border border-[#1b1d2d] bg-[#141725] p-6 text-[#f0f2ff] shadow-[0_18px_45px_rgba(0,0,0,0.45)]';

const defaultLayout: CSSProperties = {
  gridColumn: '7 / span 3',
  gridRow: '1 / span 3',
};

const overlayStyle: CSSProperties = {
  background:
    'linear-gradient(145deg, rgba(255, 205, 77, 0.24), rgba(20, 23, 37, 0.92) 62%, rgba(8, 10, 19, 0.96))',
};

export default function Box5({ className, style, children }: BoxProps) {
  const composedClassName = className ? `${baseClasses} ${className}` : baseClasses;
  const mergedStyle = style ? { ...defaultLayout, ...style } : defaultLayout;

  return (
    <section className={composedClassName} style={mergedStyle}>
      <div className="pointer-events-none absolute inset-0 rounded-[inherit]" style={overlayStyle} aria-hidden />
      {children ? (
        <div className="relative z-[1] flex flex-1 flex-col">{children}</div>
      ) : (
        <span className="relative z-[1] text-xs font-semibold uppercase tracking-[0.28em] text-[#8c90a9]">
          Box 5
        </span>
      )}
    </section>
  );
}
