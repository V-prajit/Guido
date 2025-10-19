'use client';

import GameController from '@/tempComponents/GameUI/GameController';

export default function Home() {
  return <GameController backendUrl="ws://localhost:8000" />;
}
