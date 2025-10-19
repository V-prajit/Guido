import type { ButtonHTMLAttributes, ReactNode } from 'react';

const cn = (...classes: Array<string | false | null | undefined>) =>
  classes.filter(Boolean).join(' ');

type ButtonVariant = 'primary' | 'secondary' | 'ghost';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  icon?: ReactNode;
  loading?: boolean;
}

const baseStyles =
  'group relative overflow-hidden rounded-full border px-6 py-3 text-sm font-semibold uppercase tracking-[0.28em] transition disabled:cursor-not-allowed disabled:opacity-60';

const variantStyles: Record<ButtonVariant, string> = {
  primary:
    'border-transparent bg-gradient-to-br from-[#DC0000] via-[#FF4444] to-[#DC0000] text-white shadow-[0_10px_30px_rgba(220,0,0,0.35)] hover:shadow-[0_16px_40px_rgba(220,0,0,0.45)]',
  secondary:
    'border-[#333333] bg-[#121212] text-[#f5f5f5] hover:border-[#DC0000] hover:text-white hover:shadow-[0_8px_30px_rgba(255,68,68,0.25)]',
  ghost:
    'border-transparent bg-transparent text-[#999999] hover:border-[#FFD700] hover:text-white',
};

export default function Button({
  children,
  className,
  variant = 'primary',
  icon,
  loading,
  ...props
}: ButtonProps) {
  return (
    <button className={cn(baseStyles, variantStyles[variant], className)} {...props}>
      <span className="pointer-events-none absolute inset-0 bg-[linear-gradient(120deg,rgba(255,255,255,0.35),transparent,rgba(255,255,255,0.35))] opacity-0 transition group-hover:opacity-20" />
      <span className="relative flex items-center justify-center gap-2">
        {icon && <span className="text-lg">{icon}</span>}
        <span>{loading ? 'Processing…' : children}</span>
      </span>
    </button>
  );
}
