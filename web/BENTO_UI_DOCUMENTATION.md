# F1 Strategy Gym 2026 - Bento Box UI Documentation

## Overview
A modular bento box layout for F1 Energy Management Strategy Discovery with 8 distinct sections providing real-time race insights, AI-powered strategy recommendations, and performance analytics.

## Design System

### Color Palette
- **Background**: White (`#FFFFFF`)
- **Text**: Black (`#000000`)
- **Borders**: Black (`#000000`)
- **Accents**:
  - Track: Red gradient (`#ef4444` → `#dc2626`)
  - User Car: Blue (`#3b82f6`)
  - Opponent Cars: White

### Typography
- **Headers**: Bold, uppercase, tracking-wide
- **Body**: Regular weight, readable sizing
- **Monospace**: Used for data values (speeds, times, percentages)

### Grid System
- 12-column grid layout
- 4px gap between boxes
- Responsive breakpoints for mobile/tablet

---

## Box 1: Race Track View

**Grid Span**: `col-span-3` (25% width)

**Purpose**: Real-time visualization of car positions on Bahrain International Circuit

**Features**:
- Accurate track shape from GeoJSON coordinates
- Animated car movements with realistic speed variations
- Blue highlight for user's car
- White dots for opponent cars
- Pulsing ring indicator on user car
- Corner speed reduction simulation

**Data Requirements**:
```typescript
interface CarData {
  id: string;
  driverName: string;
  position: number;
  lapProgress: number; // 0-1
  speed: number; // km/h
  lapTime: string;
  isUserCar: boolean;
}
```

**Component**: `Box1_RaceTrack.tsx`

**Dependencies**: `framer-motion`

---

## Box 2: Simulation Progress

**Grid Span**: `col-span-3` (25% width)

**Purpose**: Display ongoing simulation status and completion estimate

**Current Data**:
- Running count: 80/100 Simulations
- Progress bar: 80% complete
- Estimated completion time: 2m 15s

**Data Requirements**:
```typescript
interface SimulationProgress {
  current: number;
  total: number;
  estimatedCompletion: string;
}
```

---

## Box 3: Opponent Strategy

**Grid Span**: `col-span-3` (25% width)

**Purpose**: Display detected strategies from opponent AI agents

**Current Strategies**:
- Early Pit (Verstappen)
- Fuel Management (Hamilton)
- Tire Conservation (Leclerc)

**Data Requirements**:
```typescript
interface OpponentStrategy {
  strategy: string;
  driver: string;
  confidence?: number;
}
```

---

## Box 4: Player Telemetry

**Grid Span**: `col-span-3` (25% width)

**Purpose**: Real-time player car telemetry and status

**Metrics Displayed**:
- Lap: 15/57
- Position: P4
- Battery: 45%
- Tires: 62%
- Fuel: 28kg

**Data Requirements**:
```typescript
interface Telemetry {
  currentLap: number;
  totalLaps: number;
  position: number;
  batteryPercent: number;
  tiresPercent: number;
  fuelKg: number;
}
```

---

## Box 5: Multi-Agentic Insights (AI Confidence)

**Grid Span**: `col-span-9` (75% width)

**Purpose**: Display AI-recommended strategies with confidence scores

**Features**:
- 3 strategy cards in grid layout
- Large percentage display (win probability)
- Context-aware explanations
- Click-to-select interaction
- Hover states for better UX

**Strategy Cards**:

### 1. Aggressive Attack
- **Probability**: 75%
- **Explanation**: "Rain reduces grip advantage. Deploy power now to gain track position before conditions worsen."

### 2. Conservative Play
- **Probability**: 58%
- **Explanation**: "Maintain current pace and tire management. Wait for opponent mistakes in difficult conditions."

### 3. Balanced Drive
- **Probability**: 67%
- **Explanation**: "Moderate push with strategic overtaking. Balance risk and reward for optimal position gain."

**Data Requirements**:
```typescript
interface Strategy {
  name: string;
  probability: string; // e.g., "75%"
  explanation: string;
  selected?: boolean;
}
```

**Interaction**:
- Click to select strategy
- Selected strategy has `bg-black/5` overlay
- Hover shows `border-black` highlight

---

## Box 6: Agent Performance

**Grid Span**: `col-span-3` (25% width)

**Purpose**: Ranked comparison of agent performance vs player

**Rankings**:
1. Pure AI - P1 (98% optimal)
2. You - P2 (65% optimal)
3. Verstappen Agent - P3 (72% optimal)
4. Hamilton Agent - P4 (68% optimal)

**Data Requirements**:
```typescript
interface AgentPerformance {
  name: string;
  position: number;
  optimalPercent: number;
  isPlayer: boolean;
}
```

---

## Box 7: Decision Log

**Grid Span**: `col-span-4` (33% width)

**Purpose**: Historical record of strategic decisions and outcomes

**Entry Format**:
- Lap number with conditions (e.g., "Lap 15 (Rain)")
- Decision taken (e.g., "Aggressive Attack")
- Outcome indicator (✓ success, ✗ failure)

**Current Entries**:
- Lap 15 (Rain) - Aggressive Attack ✓
- Lap 12 (Dry) - Pit for softs ✗
- Lap 8 (Dry) - Conservative Play ✓
- Lap 3 (Dry) - Balanced Drive ✓

**Data Requirements**:
```typescript
interface Decision {
  lap: number;
  conditions: string; // "Rain" | "Dry" | "Mixed"
  decision: string;
  success: boolean;
  timestamp?: string;
}
```

**Features**:
- Scrollable list (max height: 250px)
- Newest decisions at top
- Clear success/failure indicators

---

## Box 8: Position Graph

**Grid Span**: `col-span-8` (67% width)

**Purpose**: Visualize position changes over race laps

**Current Implementation**:
- Bar chart showing 15 laps
- Stacked bars with black fill
- X-axis: Lap numbers
- Y-axis: Position

**Data Requirements**:
```typescript
interface PositionData {
  lap: number;
  position: number;
  driver?: string;
}
```

**Potential Improvements**:
- Line chart for multiple drivers
- Gap to leader visualization
- Pit stop markers
- Sector time comparisons

---

## Layout Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                  Atlassian Williams | Guido                     │
├─────────────┬─────────────┬─────────────┬─────────────────────┤
│   Box 1     │   Box 2     │   Box 3     │      Box 4          │
│ Race Track  │ Simulation  │  Opponent   │    Telemetry        │
│   View      │  Progress   │  Strategy   │                     │
├─────────────┴─────────────┴─────────────┴─────────────────────┤
│                  Box 5: Multi-Agentic Insights                 │
│   ┌──────────┬──────────┬──────────┐                          │
│   │Aggressive│Conserva- │ Balanced │   Box 6: Agent          │
│   │  Attack  │tive Play │  Drive   │   Performance           │
│   └──────────┴──────────┴──────────┘                          │
├─────────────────────────────────────┬───────────────────────────┤
│        Box 7: Decision Log          │  Box 8: Position Graph    │
│                                     │                           │
└─────────────────────────────────────┴───────────────────────────┘
```

---

## Component Architecture

### Modular Structure
Each box is a standalone component in `components/BentoBoxes/`:
- `Box1_RaceTrack.tsx`
- `Box2_Simulation.tsx`
- `Box3_OpponentStrategy.tsx`
- `Box4_Telemetry.tsx`
- `Box5_MultiAgenticInsights.tsx`
- `Box6_AgentPerformance.tsx`
- `Box7_DecisionLog.tsx`
- `Box8_PositionGraph.tsx`

### Integration
```tsx
import Box1_RaceTrack from '@/components/BentoBoxes/Box1_RaceTrack';

<div className="grid grid-cols-12 gap-4">
  <Box1_RaceTrack />
  {/* ... other boxes */}
</div>
```

---

## State Management

### Current Implementation
- Local component state using `useState`
- Mock data for demonstration

### Future Considerations
- Global state management (Redux/Zustand)
- WebSocket connections for real-time data
- Server-Sent Events for live updates
- API integration for simulation data

---

## Animation & Interactions

### Framer Motion Usage
- Car movement animations (50ms interval)
- Strategy card hover/select transitions
- Progress bar smooth updates
- Pulsing effects on user car

### User Interactions
1. **Strategy Selection**: Click any of 3 strategy cards
2. **Scrollable Logs**: Decision log with overflow-y-auto
3. **Live Updates**: All metrics update in real-time

---

## Responsive Design

### Breakpoints
- **Desktop**: 1800px max-width container
- **Tablet**: Grid adjusts to 6 columns
- **Mobile**: Stack boxes vertically

### Grid Adaptations
```tsx
// Desktop
<div className="col-span-3">...</div>

// Mobile (example)
<div className="col-span-12 md:col-span-6 lg:col-span-3">...</div>
```

---

## Performance Considerations

### Optimization Techniques
1. **Memoization**: Use `React.memo` for static boxes
2. **Virtual Scrolling**: For long decision logs
3. **Debounced Updates**: Limit animation frame rate
4. **Code Splitting**: Lazy load non-critical boxes
5. **SVG Optimization**: Simplify track path if needed

### Current Frame Rates
- Car animation: 20 FPS (50ms interval)
- Smooth for 4 cars, scalable to 20

---

## Accessibility

### Current Features
- Semantic HTML structure
- Clear color contrast (black on white)
- Keyboard navigation (strategy cards)
- ARIA labels on interactive elements

### Future Improvements
- Screen reader announcements for live updates
- High contrast mode
- Keyboard shortcuts for strategy selection
- Focus indicators

---

## Data Flow Architecture

```
Backend API
    ↓
WebSocket/SSE Connection
    ↓
React State Management
    ↓
Bento Box Components
    ↓
UI Updates (Framer Motion)
```

---

## Future Enhancements

### Short Term
1. Real API integration
2. WebSocket live data
3. More sophisticated AI explanations
4. Enhanced graph visualizations

### Long Term
1. Historical race replay
2. Strategy comparison tool
3. What-if scenario simulator
4. Export race reports
5. Multi-race season tracking

---

## Tech Stack

- **Framework**: Next.js 15
- **Styling**: Tailwind CSS
- **Animation**: Framer Motion
- **Language**: TypeScript
- **Charts**: (TBD - Recharts/Chart.js/D3)

---

## File Structure

```
web/
├── app/
│   └── page.tsx                    # Main entry point
├── components/
│   ├── BentoBoxes/
│   │   ├── Box1_RaceTrack.tsx     # ✅ Complete
│   │   ├── Box2_Simulation.tsx     # 🔄 Template
│   │   ├── Box3_OpponentStrategy.tsx
│   │   ├── Box4_Telemetry.tsx
│   │   ├── Box5_MultiAgenticInsights.tsx
│   │   ├── Box6_AgentPerformance.tsx
│   │   ├── Box7_DecisionLog.tsx
│   │   ├── Box8_PositionGraph.tsx
│   │   └── README.md              # Integration guide
│   ├── TrackAnimations/
│   │   └── SimpleTrack.tsx        # Track visualization
│   └── BentoLayout.tsx            # Main layout component
└── public/
```

---

## Version History

- **v0.1** - Initial bento box layout with 8 sections
- **v0.2** - Added Box 1 (Race Track) with real GeoJSON
- **v0.3** - Color scheme inverted to white background
- **v0.4** - Modularized components for team collaboration

---

## Contributors

- Shashank (Box 1: Race Track View)
- [Team Member 2] (Box 2: Simulation)
- [Team Member 3] (Box 3: Opponent Strategy)
- [Team Member 4] (Box 4: Telemetry)

---

## License

MIT License - F1 Strategy Gym 2026 Hackathon Project
