
# Create comprehensive interactive guide
interactive_guide = '''# Interactive Features Guide

**UAV Deconfliction System - Complete User Guide**

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Interactive CLI Mode](#interactive-cli-mode)
3. [Quick Scenario Mode](#quick-scenario-mode)
4. [Web Interface](#web-interface)
5. [Advanced Features](#advanced-features)
6. [Examples & Tutorials](#examples--tutorials)
7. [Tips & Tricks](#tips--tricks)

---

## Getting Started

### First-Time Setup

```bash
cd deconflict
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Choose Your Interface

| Interface | Best For | Complexity |
|-----------|----------|------------|
| **Interactive CLI** | Custom missions | Medium |
| **Quick Scenario** | Testing scenarios | Easy |
| **Web Interface** | Visual planning | Easy |
| **Python API** | Integration | Advanced |

---

## Interactive CLI Mode

### Starting Interactive Mode

```bash
python -m src.interactive_cli --mode interactive
```

### Step-by-Step Walkthrough

#### Step 1: Select Mode

```
1. 2D Mode (X, Y)
2. 3D Mode (X, Y, Z)

Choice (1/2): 1
```

**When to use:**
- **2D:** Most outdoor scenarios, flat terrain
- **3D:** Urban environments, different altitudes

#### Step 2: Create Primary Drone

```
CREATE PRIMARY DRONE
Enter waypoints for PRIMARY

Waypoint #1:
  X (meters): 0
  Y (meters): 0
  Add another waypoint? (y/n): y

Waypoint #2:
  X (meters): 100
  Y (meters): 50
  Add another waypoint? (y/n): n

Timing:
  Start time (sec, default 0): 0
  End time (sec): 60
  Speed (m/s, default 5.0): 5.0
```

**Tips:**
- Use realistic coordinates (meters)
- Ensure end time allows for flight at given speed
- At least 2 waypoints required

#### Step 3: Create Simulated Drones

```
CREATE SIMULATED DRONES

Number of simulated drones (1-10): 2

--- Simulated Drone 1/2 ---
(repeat waypoint entry...)
```

**Recommendations:**
- Start with 1-2 drones for testing
- Scale up to 5-10 for complex scenarios
- Keep waypoints reasonable (avoid extremes)

#### Step 4: Safety Configuration

```
SAFETY CONFIGURATION

Safety buffer (m, default 10.0): 15

Simulation accuracy:
  1. Standard (20 samples) - Fast
  2. High (50 samples) - Balanced
  3. Ultra (100 samples) - Most accurate

Choice (1-3, default 2): 2
```

**Guidelines:**
| Scenario | Buffer | Accuracy |
|----------|--------|----------|
| Testing | 10m | Standard |
| Normal ops | 15m | High |
| Critical | 20m | Ultra |

#### Step 5: Visualization

```
VISUALIZATION

1. Static plot only
2. Static + Animation
3. No visualization

Choice (1-3): 2

Save plot? (y/n): y
Filename (default: result.png): my_mission_result.png
```

**Options:**
- **Static:** Quick view, good for reports
- **Animation:** Best for understanding timing
- **None:** Fastest, report only

#### Step 6: Results & Export

```
RESULTS

✅ Mission SAFE
or
⚠️ 2 conflicts - Mission UNSAFE

Conflict #1:
  Primary: PRIMARY ↔ SIM_01
  Time: 23.45s
  Location: (45.67, 23.12)
  Distance: 8.34m < 15.00m buffer

Save mission JSON? (y/n): y
Filename: my_mission.json
```

---

## Quick Scenario Mode

### Using Quick Mode

```bash
python -m src.interactive_cli --mode quick
```

### Available Scenarios

```
1. no_conflict - Well-separated paths
2. spatial_conflict - Crossing paths
3. temporal_safe - Same path, different times
4. multiple_conflicts - Multiple collisions
5. 3d_altitude_separation - Different altitudes
6. 3d_conflict - 3D collision
```

### Example Session

```
Select scenario:
  1. no_conflict
  2. spatial_conflict
  ...

Select (1-6): 2

Buffer (m, default 10): 12

Accuracy: 1=Fast, 2=Balanced, 3=Ultra
Choice (default 2): 2

Animate? (y/n): y

Analyzing...

✗ CONFLICTS DETECTED: 1 conflict(s) found

Conflict #1:
  Primary Flight: PRIMARY_02
  Conflicting Flight: SIM_03
  Time: 20.00s
  Location: (50.00, 50.00)
  Distance: 7.07m (< 12.00m buffer)
```

---

## Web Interface

### Opening the Interface

```bash
# Option 1: Direct open
open deconflict/web_interface.html

# Option 2: Python server
cd deconflict
python -m http.server 8000
# Then visit: http://localhost:8000/web_interface.html
```

### Interface Overview

#### Header Section
- **Title:** UAV Deconfliction System
- **Subtitle:** Interactive Mission Planning

#### Sidebar (Configuration)

**Configuration Panel:**
- Mode selector (2D/3D)
- Safety buffer slider
- Accuracy dropdown

**Primary Drone Panel:**
- Waypoint list
- Add waypoint button
- Timing inputs
- Speed configuration

**Simulated Drones Panel:**
- Drone count selector
- Drone list
- Edit buttons

**Action Buttons:**
- Run Analysis (primary button)
- Load Scenario
- Export Data

#### Main Panel

**Statistics Cards:**
- Primary waypoints count
- Simulated drones count
- Conflicts detected

**Canvas:**
- Visual path display
- Grid background
- Color-coded routes

**Results Panel:**
- Analysis output
- Conflict details
- Status indicators

### Using the Web Interface

#### 1. Configure Mission

```
1. Select mode (2D/3D)
2. Set safety buffer
3. Choose accuracy level
```

#### 2. Create Primary Path

```
1. Click waypoint inputs
2. Enter X, Y coordinates
3. (Optional) Enter Z for 3D
4. Click "+ Add Waypoint" for more
5. Set start/end times
```

#### 3. Configure Simulated Drones

```
1. Adjust "Number of Drones" slider
2. (Optional) Click "Edit" on each drone
3. Configure waypoints and timing
```

#### 4. Run Analysis

```
1. Click "🚀 Run Analysis"
2. View results in results panel
3. Check statistics cards
4. Examine canvas visualization
```

#### 5. Export Data

```
1. Click "💾 Export Data"
2. Browser downloads mission_data.json
3. Use file with Python API
```

---

## Advanced Features

### High-Accuracy Simulation

```python
from src.detector_enhanced import check_mission_high_accuracy

# Ultra-high precision (200 samples)
is_clear, conflicts = check_mission_high_accuracy(
    primary, simulated,
    safety_buffer=10.0,
    include_z=False,
    time_samples=200  # Custom sample count
)
```

### Custom Visualization

```python
from src.viz import plot_2d_trajectories
import matplotlib.pyplot as plt

# Create custom plot
fig, ax = plot_2d_trajectories(
    primary, simulated, conflicts,
    safety_buffer=15.0,
    figsize=(16, 12)  # Larger figure
)

# Customize
ax.set_title("My Custom Mission Analysis", fontsize=20)
ax.grid(True, linestyle=':', alpha=0.5)

# Save with high DPI
fig.savefig('custom_plot.png', dpi=300)
plt.show()
```

### Batch Processing

```python
import json
from src.data_models import load_flight_from_dict
from src.detector_enhanced import check_mission_high_accuracy

# Load multiple missions
mission_files = ['mission1.json', 'mission2.json', 'mission3.json']

results = []
for file in mission_files:
    with open(file) as f:
        data = json.load(f)
    
    primary = load_flight_from_dict(data['primary'])
    simulated = [load_flight_from_dict(f) for f in data['simulated']]
    
    is_clear, conflicts = check_mission_high_accuracy(
        primary, simulated, time_samples=100
    )
    
    results.append({
        'file': file,
        'safe': is_clear,
        'conflicts': len(conflicts)
    })

# Summary
for result in results:
    status = "✅ SAFE" if result['safe'] else "⚠️  UNSAFE"
    print(f"{result['file']}: {status} ({result['conflicts']} conflicts)")
```

---

## Examples & Tutorials

### Example 1: Simple Crossing Paths

```python
from src.data_models import Flight, Waypoint
from src.detector_enhanced import check_mission_high_accuracy
from src.viz import plot_2d_trajectories

# Primary: horizontal flight
primary = Flight(
    id="PRIMARY",
    waypoints=[Waypoint(0, 50), Waypoint(100, 50)],
    t_start=0, t_end=40
)

# Simulated: vertical flight
simulated = [
    Flight(
        id="SIM_01",
        waypoints=[Waypoint(50, 0), Waypoint(50, 100)],
        t_start=10, t_end=50
    )
]

# Check with high accuracy
is_clear, conflicts = check_mission_high_accuracy(
    primary, simulated,
    safety_buffer=10.0,
    time_samples=100
)

print(f"Safe: {is_clear}")
print(f"Conflicts: {len(conflicts)}")

# Visualize
plot_2d_trajectories(primary, simulated, conflicts)
```

### Example 2: 3D Mission with Altitude Separation

```python
# Primary: low altitude
primary = Flight(
    id="PRIMARY",
    waypoints=[
        Waypoint(0, 0, 50),
        Waypoint(100, 100, 50)
    ],
    t_start=0, t_end=60
)

# Simulated: high altitude (safe)
simulated = [
    Flight(
        id="SIM_01",
        waypoints=[
            Waypoint(0, 100, 100),  # 50m higher
            Waypoint(100, 0, 100)
        ],
        t_start=0, t_end=60
    )
]

# 2D check (will show conflict)
is_clear_2d, _ = check_mission_high_accuracy(
    primary, simulated, include_z=False
)

# 3D check (will be clear)
is_clear_3d, _ = check_mission_high_accuracy(
    primary, simulated, include_z=True
)

print(f"2D check: {is_clear_2d}")  # False
print(f"3D check: {is_clear_3d}")  # True
```

### Example 3: Interactive Mission Builder

```python
def build_mission_interactive():
    """Build mission with prompts."""
    waypoints = []
    
    while True:
        x = float(input("X: "))
        y = float(input("Y: "))
        z = float(input("Z (0 for 2D): "))
        
        waypoints.append(Waypoint(x, y, z))
        
        if len(waypoints) >= 2:
            if input("More? (y/n): ").lower() != 'y':
                break
    
    t_start = float(input("Start time: "))
    t_end = float(input("End time: "))
    
    return Flight(
        id="CUSTOM",
        waypoints=waypoints,
        t_start=t_start,
        t_end=t_end
    )

# Use it
primary = build_mission_interactive()
```

---

## Tips & Tricks

### For Better Accuracy

1. **Use More Samples for Critical Checks**
   ```python
   # Critical mission
   check_mission_high_accuracy(..., time_samples=200)
   ```

2. **Tighten Buffer for Dense Airspace**
   ```python
   # Urban environment
   safety_buffer = 20.0  # instead of 10.0
   ```

3. **Account for Drone Size**
   ```python
   # Large drones
   drone_radius = 2.0  # meters
   safety_buffer = 10.0 + (2 * drone_radius)
   ```

### For Better Performance

1. **Use Standard Mode for Testing**
   ```python
   # Quick test
   check_mission(..., time_samples=20)
   
   # Final validation
   check_mission_high_accuracy(..., time_samples=100)
   ```

2. **Limit Simulated Drones**
   - Start with 1-2 drones
   - Add more as needed
   - Performance: O(n × m) where n=primary segments, m=sim segments

3. **Pre-filter by Time**
   ```python
   # Only check drones with overlapping time windows
   relevant_sims = [
       s for s in simulated
       if not (s.t_end < primary.t_start or s.t_start > primary.t_end)
   ]
   ```

### For Better Visualizations

1. **Adjust Figure Size**
   ```python
   plot_2d_trajectories(..., figsize=(16, 12))
   ```

2. **Save High-Resolution**
   ```python
   save_visualization(fig, 'result.png', dpi=300)
   ```

3. **Customize Animation Speed**
   ```python
   anim = animate_2d_trajectories(..., dt=0.05)  # Slower, smoother
   ```

---

## Keyboard Shortcuts

### Interactive CLI

| Key | Action |
|-----|--------|
| `Ctrl+C` | Cancel/Exit |
| `Enter` | Confirm input |
| `y` | Yes |
| `n` | No |

### Web Interface

| Action | Shortcut |
|--------|----------|
| Run Analysis | `Alt+R` (if implemented) |
| Export Data | `Ctrl+S` (browser default) |
| Refresh | `F5` |

---

## Common Issues & Solutions

### Issue: "Need at least 2 waypoints"

**Solution:** Add more waypoints before removing existing ones.

### Issue: "End time must be > start time"

**Solution:** Ensure t_end > t_start. Check your inputs.

### Issue: Animation not showing

**Solution:**
1. Check if matplotlib backend supports animation
2. Install pillow: `pip install pillow`
3. Try saving to GIF instead of displaying

### Issue: Web interface blank

**Solution:**
1. Open browser console (F12)
2. Check for JavaScript errors
3. Ensure file is opened as `file://` or via local server
4. Try different browser

---

## Best Practices

### Mission Planning

1. **Start Simple:** 2-3 waypoints first
2. **Validate Inputs:** Check coordinates make sense
3. **Test Incrementally:** Add drones one at a time
4. **Document Everything:** Save JSON configs

### Safety Configuration

1. **Conservative Buffers:** Err on side of caution
2. **Match Environment:** Urban > Rural buffers
3. **Consider Speed:** Faster drones need more buffer
4. **Account for Errors:** GPS accuracy ±5m

### Development Workflow

1. **Quick Test:** Standard accuracy (20 samples)
2. **Validation:** High accuracy (50 samples)
3. **Final Check:** Ultra accuracy (100 samples)
4. **Documentation:** Save plots and configs

---

## Next Steps

**Beginner:**
1. Try interactive CLI with simple 2-waypoint mission
2. Test all pre-built scenarios
3. Experiment with safety buffers

**Intermediate:**
1. Create custom multi-waypoint missions
2. Test 3D scenarios
3. Export and modify JSON configs

**Advanced:**
1. Integrate with external systems
2. Implement custom scenarios
3. Extend with new features
4. Build automated testing pipelines

---

**Happy Flying! 🚁**
'''

with open("deconflict/INTERACTIVE_GUIDE.md", "w") as f:
    f.write(interactive_guide)

print("✓ Created INTERACTIVE_GUIDE.md")
print("\n" + "="*70)
print("INTERACTIVE VERSION COMPLETE!")
print("="*70)
