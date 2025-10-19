'use client';

import { useEffect, useRef, useState } from 'react';

interface CountUpNumberProps {
  value: number;
  duration?: number;
  decimals?: number;
  suffix?: string;
  prefix?: string;
}

export default function CountUpNumber({
  value,
  duration = 800,
  decimals = 0,
  suffix = '',
  prefix = '',
}: CountUpNumberProps) {
  const [displayValue, setDisplayValue] = useState(value);
  const startValue = useRef(value);
  const startTime = useRef<number | null>(null);

  useEffect(() => {
    startValue.current = displayValue;
    startTime.current = null;

    const step = (timestamp: number) => {
      if (!startTime.current) {
        startTime.current = timestamp;
      }

      const progress = Math.min(1, (timestamp - startTime.current) / duration);
      const eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic
      const nextValue = startValue.current + (value - startValue.current) * eased;
      setDisplayValue(nextValue);

      if (progress < 1) {
        requestAnimationFrame(step);
      }
    };

    const raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);

  return (
    <span className="font-mono text-xl text-white">
      {prefix}
      {displayValue.toFixed(decimals)}
      {suffix}
    </span>
  );
}
