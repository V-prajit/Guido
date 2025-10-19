'use client';

import { Box1, Box2, Box3, Box4, Box5, Box6, Box7, Box8 } from './components/Box';
import { Logo } from './components/Logo';

export default function Home() {
  return (
    <main className="flex h-screen w-screen overflow-hidden p-4">
      <div
        className="grid h-full w-full gap-6"
        style={{
          gridTemplateColumns: 'repeat(12, minmax(0, 1fr))',
          gridTemplateRows: 'repeat(12, minmax(0, 1fr))',
        }}
      >
        <Logo />
        <Box1 />
        <Box2 />
        <Box3 />
        <Box4 />
        <Box5 />
        <Box6 />
        <Box7 />
        <Box8 />
      </div>
    </main>
  );
}
