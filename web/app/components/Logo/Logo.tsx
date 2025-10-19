import type { CSSProperties } from 'react';

export default function Logo() {
  const logoStyle: CSSProperties = {
    gridColumn: '1 / span 3',
    gridRow: '1 / span 2',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 10,
    transform: 'translateY(-2.5rem)',
  };

  const textStyle: CSSProperties = {
    fontSize: '3.5rem',
    fontWeight: 'bold',
    fontFamily: 'serif',
    color: '#FFD700',
    textShadow: '0px 0px 10px rgba(0,0,0,0.2)',
    textDecoration: 'underline',
  };

  return (
    <div style={logoStyle}>
      <h1 style={textStyle}>Guido🏎️</h1>
    </div>
  );
}
