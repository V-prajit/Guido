import type { CSSProperties } from 'react';

export default function Logo() {
  const logoStyle: CSSProperties = {
    gridColumn: '1 / span 3',
    gridRow: '1 / span 2',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 10,
    transform: 'translateY(-2rem)',
  };

  const textStyle: CSSProperties = {
    fontSize: '3.5rem',
    fontWeight: 900,
    fontFamily: "'Orbitron', sans-serif",
    color: '#e6edf3',
    textShadow: '0px 0px 10px rgba(0,0,0,0.2)',
  };

  return (
    <div style={logoStyle}>
      <h1 style={{...textStyle, display: 'flex', alignItems: 'center' }}>
        Guido
        <img
          src="/guido.png"
          alt="Guido"
          style={{
            height: '5rem',
            marginLeft: '-1.5rem',
          }}
        />
      </h1>
    </div>
  );
}
