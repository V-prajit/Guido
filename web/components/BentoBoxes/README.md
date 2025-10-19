# Bento Boxes - Modular Components

This folder contains standalone bento box components that can be easily integrated and merged between team members.

## Box 1: Race Track View

**File:** `Box1_RaceTrack.tsx`

**Owner:** Shashank

**Description:** Real-time F1 race track visualization using actual Bahrain International Circuit GeoJSON coordinates with animated car positions.

### Integration

```tsx
import Box1_RaceTrack from '@/components/BentoBoxes/Box1_RaceTrack';

// In your layout
<Box1_RaceTrack />

// With custom car data
<Box1_RaceTrack cars={yourCarData} />
```

### Dependencies
- `framer-motion`

### Props
| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `cars` | `CarData[]` | No | MOCK_CARS | Array of car positions and data |

### CarData Interface
```typescript
interface CarData {
  id: string;           // Unique identifier
  driverName: string;   // Driver name
  position: number;     // Race position (1-20)
  lapProgress: number;  // 0 to 1 (lap completion)
  speed: number;        // Current speed in km/h
  lapTime: string;      // Formatted lap time
  isUserCar: boolean;   // Highlight as user's car
}
```

### Styling
- Background: White with black border
- Track: Red gradient (from GeoJSON)
- User car: Blue
- Opponent cars: White
- Size: `col-span-3` (25% width in 12-column grid)

---

## Box 2-8: [Reserved for team members]

### Template for adding new boxes

**File:** `Box{N}_{Name}.tsx`

**Owner:** [Your Name]

**Description:** [Brief description]

### Integration
```tsx
import Box{N}_{Name} from '@/components/BentoBoxes/Box{N}_{Name}';
<Box{N}_{Name} />
```

---

## Grid Layout Reference

Our bento box layout uses a 12-column grid:

```tsx
<div className="grid grid-cols-12 gap-4">
  <Box1_RaceTrack />       {/* col-span-3 */}
  <Box2_Simulation />      {/* col-span-3 */}
  <Box3_Opponent />        {/* col-span-3 */}
  <Box4_Telemetry />       {/* col-span-3 */}
</div>
```

### Common Span Sizes
- `col-span-3` = 25% width (1/4)
- `col-span-4` = 33% width (1/3)
- `col-span-6` = 50% width (1/2)
- `col-span-9` = 75% width (3/4)
- `col-span-12` = 100% width (full)

---

## Merging Guidelines

1. **Each person works on their assigned box(es)**
2. **Keep components self-contained** - all logic inside the component file
3. **Use consistent naming**: `Box{N}_{Name}.tsx`
4. **Document your component** in this README
5. **Test independently** before merging
6. **Props interface** should be exported for type safety

### Git Workflow
```bash
# Create your box file
touch components/BentoBoxes/Box2_YourBox.tsx

# Work on your branch
git checkout -b box2-yourname

# Commit only your box
git add components/BentoBoxes/Box2_YourBox.tsx
git commit -m "Add Box 2: Your Box Name"

# Push and create PR
git push origin box2-yourname
```

---

## Current Box Assignments

| Box # | Component | Owner | Status |
|-------|-----------|-------|--------|
| 1 | Race Track View | Shashank | ✅ Complete |
| 2 | Simulation Progress | [Name] | 🔄 In Progress |
| 3 | Opponent Strategy | [Name] | ⏳ Pending |
| 4 | Player Telemetry | [Name] | ⏳ Pending |
| 5 | AI Confidence | [Name] | ⏳ Pending |
| 6 | Agent Performance | [Name] | ⏳ Pending |
| 7 | Decision Log | [Name] | ⏳ Pending |
| 8 | Position Graph | [Name] | ⏳ Pending |
