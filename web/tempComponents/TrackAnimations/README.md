# F1 Bahrain Track Animation - DataTrack Component

## Overview

A production-ready, data-driven F1 track animation component built with React, TypeScript, and Framer Motion. Features broadcast-quality HUD elements, real-time telemetry displays, and smooth car animations on the Bahrain International Circuit.

## Features

### Visual Elements
- **RED Track Circuit**: Gradient stroke with glow effects and sector divisions
- **BLUE Player Car**: Highlighted with speed display and enhanced visibility
- **WHITE Opponent Cars**: Minimalist design with driver codes
- **Sector Zones**: S1, S2, S3 indicators with active state animations
- **HUD Components**:
  - Left Panel: Detailed telemetry for selected car
  - Right Panel: Live standings leaderboard
  - Bottom Panel: Race controls and car selection
  - Top Panel: Circuit and race information

### Data Points Tracked

#### Real-time Telemetry
```typescript
interface CarTelemetry {
  // Identity
  id: string
  driverName: string
  driverCode: string
  teamColor: string
  position: number

  // Vehicle Dynamics
  speed: number           // KPH
  throttle: number        // 0-100%
  brake: number           // 0-100%
  gear: number            // 1-8
  rpm: number             // Current RPM

  // Race Systems
  drs: boolean            // DRS active/inactive
  ers: number             // ERS charge 0-100%

  // Timing
  currentSector: 1 | 2 | 3
  sectorTimes: SectorTime[]
  lapTime: number         // Total lap time in seconds
  gap: string             // Gap to leader or position ahead

  // Tyres
  tyreCompound: 'SOFT' | 'MEDIUM' | 'HARD' | 'INTER' | 'WET'
  tyreLaps: number        // Age of current tyres

  // Position
  trackPosition: Position // x, y, angle on track
}
```

#### Sector Timing
```typescript
interface SectorTime {
  sector: 1 | 2 | 3
  time: number
  status: 'personal-best' | 'fastest' | 'normal' | 'slower'
}
```

## Data Integration Approach

### 1. Mock Data (Current Implementation)

The component currently uses `generateMockTelemetry()` to simulate realistic race data:

```typescript
const telemetry = generateMockTelemetry(carId, isPlayer, lapProgress);
```

**Mock data includes:**
- Randomized but realistic speed variations (280-350 KPH)
- Dynamic throttle/brake inputs
- Gear changes based on track position
- Sector time variations with status indicators
- ERS depletion and DRS activation
- Tyre compound selection and wear

### 2. Real Data Integration

To connect real F1 data sources, replace the mock generator with API calls:

#### Option A: WebSocket Stream (Real-time)
```typescript
useEffect(() => {
  const ws = new WebSocket('wss://your-f1-data-api.com/live');

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    setCarTelemetries(data.cars.map(transformAPIData));
  };

  return () => ws.close();
}, []);
```

#### Option B: REST API Polling
```typescript
useEffect(() => {
  const fetchTelemetry = async () => {
    const response = await fetch('/api/f1/telemetry');
    const data = await response.json();
    setCarTelemetries(data);
  };

  const interval = setInterval(fetchTelemetry, 100); // 10Hz update
  return () => clearInterval(interval);
}, []);
```

#### Option C: F1 Game Telemetry (UDP)
For F1 game data (F1 2024, etc.), use a Node.js UDP server:

```typescript
// Server-side (Node.js)
const dgram = require('dgram');
const server = dgram.createSocket('udp4');

server.on('message', (msg, rinfo) => {
  const telemetry = parseF1Packet(msg);
  io.emit('telemetry', telemetry); // Broadcast via Socket.io
});

// Client-side (React)
useEffect(() => {
  socket.on('telemetry', (data) => {
    setCarTelemetries(transformGameData(data));
  });
}, []);
```

### 3. Data Transformation

Create adapter functions to transform external data to the component's format:

```typescript
const transformAPIData = (apiCar: any): CarTelemetry => ({
  id: apiCar.driver_id,
  driverName: apiCar.driver_name,
  driverCode: apiCar.driver_abbreviation,
  teamColor: TEAM_COLORS[apiCar.team],
  position: apiCar.position,
  speed: apiCar.speed,
  throttle: apiCar.throttle_percentage,
  brake: apiCar.brake_percentage,
  gear: apiCar.gear,
  rpm: apiCar.engine_rpm,
  drs: apiCar.drs_active,
  ers: apiCar.ers_charge,
  currentSector: apiCar.current_sector,
  sectorTimes: apiCar.sector_times,
  lapTime: apiCar.current_lap_time,
  gap: apiCar.gap_to_leader,
  tyreCompound: apiCar.tyre_compound,
  tyreLaps: apiCar.tyre_age,
  trackPosition: calculateTrackPosition(apiCar.track_progress)
});
```

### 4. Track Position Calculation

For accurate car positioning, implement path following:

```typescript
const calculateTrackPosition = (progressPercent: number): Position => {
  const path = document.getElementById('track-path') as SVGPathElement;
  if (!path) return { x: 0, y: 0, angle: 0 };

  const pathLength = path.getTotalLength();
  const point = path.getPointAtLength((progressPercent / 100) * pathLength);
  const nextPoint = path.getPointAtLength(
    ((progressPercent + 0.1) / 100) * pathLength
  );

  const angle = Math.atan2(
    nextPoint.y - point.y,
    nextPoint.x - point.x
  ) * (180 / Math.PI);

  return { x: point.x, y: point.y, angle };
};
```

## Component Architecture

### State Management
```typescript
const [lapProgress, setLapProgress] = useState(0);
const [carTelemetries, setCarTelemetries] = useState<CarTelemetry[]>([]);
const [selectedCarId, setSelectedCarId] = useState('1');
const [isPaused, setIsPaused] = useState(false);
```

### Sub-Components

1. **SectorIndicator**: Circular sector markers (S1, S2, S3) with pulse animation
2. **CarMarker**: Animated car icons with position and speed labels
3. **TelemetryHUD**: Comprehensive left-side panel with all car data
4. **LeaderboardHUD**: Right-side standings with live gaps

## Customization

### Track Layout
Modify `BAHRAIN_TRACK_PATH` to change circuit shape:
```typescript
const BAHRAIN_TRACK_PATH = `M 120 300 L 180 300 ...`;
```

### Sector Divisions
Adjust sector percentages:
```typescript
const SECTOR_ZONES: SectorZone[] = [
  { id: 1, startPercent: 0, endPercent: 35, label: 'S1' },
  { id: 2, startPercent: 35, endPercent: 68, label: 'S2' },
  { id: 3, startPercent: 68, endPercent: 100, label: 'S3' },
];
```

### Animation Speed
Change update frequency:
```typescript
const interval = setInterval(() => {
  setLapProgress((prev) => (prev + 0.5) % 100); // Adjust 0.5 for speed
}, 50); // Adjust interval for smoothness
```

### Colors & Theme
All colors are defined inline for easy customization:
- Player car: `#3B82F6` (blue)
- Track: `#DC2626` (red)
- Opponent cars: `#FFFFFF` (white)
- HUD backgrounds: `black/90` with backdrop blur

## Performance Optimization

1. **Memoization**: Wrap sub-components with `React.memo()` for expensive renders
2. **Animation throttling**: Use `requestAnimationFrame` instead of `setInterval`
3. **SVG optimization**: Reduce path complexity for smoother rendering
4. **State updates**: Batch telemetry updates using `useReducer`

```typescript
// Optimized animation loop
useEffect(() => {
  let animationId: number;

  const animate = () => {
    setLapProgress(prev => (prev + 0.5) % 100);
    animationId = requestAnimationFrame(animate);
  };

  animationId = requestAnimationFrame(animate);
  return () => cancelAnimationFrame(animationId);
}, []);
```

## Usage Example

```tsx
import { DataTrack } from '@/components/TrackAnimations/DataTrack';

export default function RacePage() {
  return (
    <div className="w-full h-screen">
      <DataTrack />
    </div>
  );
}
```

## API Integration Examples

### F1 Live Timing API
```typescript
const F1_API_BASE = 'https://api.openf1.org/v1';

const fetchLiveTelemetry = async (sessionKey: string) => {
  const [cars, telemetry] = await Promise.all([
    fetch(`${F1_API_BASE}/position?session_key=${sessionKey}`),
    fetch(`${F1_API_BASE}/car_data?session_key=${sessionKey}`)
  ]);

  const positionData = await cars.json();
  const telemetryData = await telemetry.json();

  return mergeTelemetryData(positionData, telemetryData);
};
```

### FastF1 Python Backend
```python
# backend.py
import fastf1
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/telemetry/<session>')
def get_telemetry(session):
    session = fastf1.get_session(2024, 'Bahrain', 'R')
    session.load()

    laps = session.laps
    telemetry = []

    for driver in session.drivers:
        car_data = laps.pick_driver(driver).get_car_data()
        telemetry.append({
            'driver': driver,
            'speed': car_data['Speed'].tolist(),
            'throttle': car_data['Throttle'].tolist(),
            # ... more data
        })

    return jsonify(telemetry)
```

## Data Sources

### Recommended APIs
1. **OpenF1 API** (https://openf1.org) - Free, real-time F1 data
2. **Ergast API** (http://ergast.com/mrd/) - Historical F1 data
3. **F1 Game UDP Telemetry** - Direct from F1 2024 game
4. **FastF1 Python Library** - Comprehensive telemetry analysis

### Mock Data for Testing
The component includes comprehensive mock data generation that simulates:
- Realistic speed curves (200-350 KPH)
- Proper sector timing (S1: 27-28s, S2: 35-36s, S3: 29-30s)
- Dynamic ERS charge/depletion
- Strategic DRS activation zones
- Tyre degradation over laps

## Extending the Component

### Add More Telemetry Points
```typescript
interface ExtendedTelemetry extends CarTelemetry {
  fuelLoad: number;
  brakeTemp: [number, number, number, number];
  tyreTemp: [number, number, number, number];
  downforce: number;
  engineMode: 'FULL' | 'MEDIUM' | 'LOW';
}
```

### Add Weather Overlay
```typescript
<motion.div className="absolute top-20 right-4">
  <WeatherWidget
    temperature={38}
    trackTemp={52}
    humidity={45}
    windSpeed={12}
  />
</motion.div>
```

### Add Pit Stop Indicator
```typescript
{car.inPitLane && (
  <motion.circle
    cx={car.trackPosition.x}
    cy={car.trackPosition.y - 30}
    r={10}
    fill="#F59E0B"
    animate={{ scale: [1, 1.2, 1] }}
    transition={{ repeat: Infinity, duration: 1 }}
  />
)}
```

## Browser Compatibility

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support (requires Framer Motion 8+)
- Mobile: Responsive design, touch controls supported

## License

Component is part of the F1 simulation project. Ensure compliance with F1 trademark usage.
