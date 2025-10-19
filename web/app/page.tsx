'use client';

import { useState } from 'react';
import BentoLayout from '../components/BentoLayout';

export default function Home() {
  const [activeTab, setActiveTab] = useState('bento');

  return (
    <main className="min-h-screen bg-white">
      <header className="pt-6 pb-4 px-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-black tracking-wider">Atlassian Williams | Guido</h1>
        </div>
        <div className="w-full h-[1px] bg-black/20 mt-4"></div>
      </header>

      {activeTab === 'bento' && <BentoLayout />}
    </main>
  );
}
