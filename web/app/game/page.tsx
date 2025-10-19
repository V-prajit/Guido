/**
 * Game Mode Page
 *
 * Interactive racing game with AI opponents and strategic decision points.
 */

import GameController from "@/components/GameUI/GameController";

export default function GamePage() {
  return <GameController backendUrl="ws://localhost:8000" />;
}
