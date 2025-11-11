# UAV Strategic Deconfliction System

**FlytBase Robotics Assignment 2025**

A comprehensive system for verifying whether a drone's planned waypoint mission is safe to execute in shared airspace by detecting spatio-temporal conflicts with other drone flights.

---

## 🎯 Features

- **Spatial Conflict Detection**: Validates minimum safety distances between flight paths
- **Temporal Conflict Checking**: Only flags conflicts when drones occupy the same space at overlapping times
- **2D and 3D Support**: Handles both planar and altitude-aware flight paths (3D for extra credit)
- **Multiple Conflict Scenarios**: Pre-built test scenarios including no-conflict, spatial conflict, temporal separation, and more
- **Rich Visualizations**: 
  - ✨ **Enhanced Static 2D/3D Plots**: Modern aesthetics with professional color schemes, improved typography, and polished styling
  - 🎬 **Smooth Animations**: Enhanced animated trajectory playback with better visual effects
  - 🖱️ **Interactive Plotly Visualizations**: Hover-enabled 2D plots with detailed information
  - ⏱️ **4D Time-Slider Visualization**: Interactive 3D + time visualization with play/pause controls (extra credit)
  - 🎮 **Interactive Dashboard**: Full-featured dashboard with status indicators, conflict tables, and manual controls
  - 🎨 **Semantic Color Coding**: Intuitive colors (green=safe, yellow=warning, red=danger) with severity levels
  - 📊 **Safety Buffer Visualization**: Clear conflict highlighting with gradient effects
  - 🚦 **Real-time Status Indicators**: Visual feedback for mission clearance status
- **Comprehensive Testing**: Unit tests, integration tests, and automated test scenarios
- **Easy-to-Use CLI**: Command-line interface with multiple visualization options
- **Modular Architecture**: Clean separation of concerns for maintainability and extensibility

---

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

```bash
# Clone or download the project
cd deconflict

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

---

## 🚀 Quick Start

### Using Built-in Scenarios

```bash
# Run a scenario with no conflicts
python -m src.cli --scenario no_conflict

# Run a scenario with spatial conflicts
python -m src.cli --scenario spatial_conflict

# Run with custom safety buffer
python -m src.cli --scenario multiple_conflicts --buffer 15.0

# Enable 3D checking
python -m src.cli --scenario 3d_conflict --3d

# Generate animation
python -m src.cli --scenario spatial_conflict --animate

# Generate interactive Plotly visualization (2D)
python -m src.cli --scenario spatial_conflict --interactive

# Generate 4D time-slider visualization (3D + time)
python -m src.cli --scenario 3d_conflict --3d --time-slider

# Generate interactive dashboard with manual controls
python -m src.cli --scenario spatial_conflict --dashboard

# Save visualization
python -m src.cli --scenario spatial_conflict --output results.png
```

### Using Custom Flight Data

Create a JSON file (`my_mission.json`):

```json
{
  "primary": {
    "id": "DRONE_PRIMARY",
    "waypoints": [
      {"x": 0, "y": 0, "z": 50},
      {"x": 100, "y": 100, "z": 50}
    ],
    "t_start": 0.0,
    "t_end": 60.0,
    "speed": 5.0
  },
  "simulated": [
    {
      "id": "DRONE_SIM_01",
      "waypoints": [
        {"x": 100, "y": 0, "z": 50},
        {"x": 0, "y": 100, "z": 50}
      ],
      "t_start": 0.0,
      "t_end": 60.0,
      "speed": 5.0
    }
  ]
}
```

Run the check:

```bash
python -m src.cli --input my_mission.json --buffer 10.0 --3d
```

---

## 🧩 Architecture

### Project Structure

```
deconflict/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── src/
│   ├── __init__.py          # Package initialization
│   ├── data_models.py       # Core data structures (Flight, Waypoint, Segment, Conflict)
│   ├── trajectory.py        # Trajectory interpolation and segment building
│   ├── detector.py          # Collision detection algorithms
│   ├── viz.py               # Visualization functions
│   ├── example_scenarios.py # Pre-built test scenarios
│   └── cli.py               # Command-line interface
├── tests/
│   ├── test_trajectory.py   # Unit tests for trajectory module
│   ├── test_detector.py     # Unit tests for detector module
│   └── test_integration.py  # Integration tests
├── docs/
│   └── reflection.md        # Design reflection and documentation
└── demo_video/
    └── script.md            # Demo video script
```

### Core Modules

#### 1. `data_models.py`
Defines core data structures:
- **Waypoint**: Represents a point in 2D/3D space
- **Flight**: Complete mission with waypoints and timing
- **Segment**: Linear path between two waypoints with time bounds
- **Conflict**: Detected collision with location, time, and details

#### 2. `trajectory.py`
Handles trajectory generation:
- Time allocation across waypoints based on path length
- Segment generation from waypoints
- Position interpolation at arbitrary time points
- Velocity and speed calculations

#### 3. `detector.py`
Core conflict detection logic:
- Temporal overlap checking
- Spatio-temporal distance computation
- Pairwise segment conflict detection
- Complete mission validation

#### 4. `viz.py`
Visualization capabilities:
- 2D static trajectory plots
- 3D trajectory visualization
- Animated trajectory playback
- Conflict highlighting with safety buffers

---

## 🧪 Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_detector.py -v

# Run with coverage report
python -m pytest tests/ --cov=src --cov-report=html

# Run individual test modules
python -m unittest tests.test_trajectory
python -m unittest tests.test_detector
python -m unittest tests.test_integration
```

---

## 📊 Algorithm Details

### Conflict Detection Strategy

The system uses a **4D spatio-temporal conflict detection** approach:

1. **Segment Generation**: 
   - Convert waypoint missions into linear segments
   - Allocate time proportionally to segment length

2. **Temporal Filtering**:
   - Check if segment time windows overlap
   - Skip spatial checks if no temporal overlap

3. **Spatial Sampling**:
   - For overlapping time windows, sample positions at regular intervals
   - Compute Euclidean distance at each sample point
   - Track minimum distance and location

4. **Conflict Reporting**:
   - Flag conflict if minimum distance < safety buffer
   - Report conflicting flights, location, time, and distance

### Time Complexity

- **Per segment pair**: O(k) where k is number of time samples (default: 20)
- **Overall**: O(n × m × k) where:
  - n = number of primary segments
  - m = total segments in all simulated flights
  - k = time samples per check

### Accuracy vs. Performance

- Default: 20 time samples per segment pair (good balance)
- Increase for higher accuracy: `time_samples=50` in `segment_conflict()`
- Decrease for faster checks: `time_samples=10`

---

## 🎓 Built-in Test Scenarios

| Scenario | Description | Expected Result |
|----------|-------------|-----------------|
| `no_conflict` | Well-separated paths | ✓ Clear |
| `spatial_conflict` | Crossing paths, overlapping time | ✗ Conflict |
| `temporal_safe` | Crossing paths, separated time | ✓ Clear |
| `multiple_conflicts` | Multiple drones with conflicts | ✗ Multiple conflicts |
| `3d_altitude_separation` | Paths cross but different altitudes | ✓ Clear (3D mode) |
| `3d_conflict` | Paths cross at same altitude | ✗ Conflict |

---

## 🔧 Extending the System

### Adding New Scenarios

```python
from src.data_models import Flight, Waypoint

def my_custom_scenario():
    primary = Flight(
        id="CUSTOM_PRIMARY",
        waypoints=[Waypoint(0, 0), Waypoint(100, 100)],
        t_start=0.0,
        t_end=50.0
    )

    simulated = [
        Flight(
            id="CUSTOM_SIM",
            waypoints=[Waypoint(100, 0), Waypoint(0, 100)],
            t_start=0.0,
            t_end=50.0
        )
    ]

    return primary, simulated
```

### Custom Analysis

```python
from src import check_mission, plot_2d_trajectories

primary, simulated = my_custom_scenario()

# Run check
is_clear, conflicts = check_mission(
    primary, simulated,
    safety_buffer=15.0,
    include_z=False
)

# Visualize
if not is_clear:
    plot_2d_trajectories(primary, simulated, conflicts)
```

---

## 📈 Scaling Considerations

### Current Limitations
- In-memory processing
- Sequential conflict checking
- Limited to small-scale scenarios (< 100 drones)

### Scalability Enhancements for Production

1. **Spatial Indexing**:
   - Implement R-tree or quadtree for spatial queries
   - Reduce O(n²) pairwise checks to O(n log n)

2. **Time-based Partitioning**:
   - Divide airspace into time slots
   - Only check flights with temporal overlap

3. **Distributed Processing**:
   - Parallelize conflict checks across drone pairs
   - Use Apache Spark or Ray for distributed computation

4. **Real-time Updates**:
   - Implement streaming conflict detection
   - Use message queues (Kafka, RabbitMQ) for flight updates

5. **Approximate Methods**:
   - Use bounding volumes (spheres, boxes) for fast rejection
   - Detailed checks only for potential conflicts

6. **Database Integration**:
   - Store flight plans in spatial database (PostGIS)
   - Leverage built-in spatial queries

---

## 🤖 AI-Assisted Development

This project extensively used AI coding assistants (Claude, GitHub Copilot) to accelerate development. Key applications:

### Code Generation
- **Prompt**: "Generate trajectory interpolation function with linear interpolation between waypoints"
- **Output**: Initial implementation of `interpolate_trajectory()`
- **Refinement**: Added time-based sampling and 3D support

### Test Case Generation
- **Prompt**: "Create unit tests for segment conflict detection covering edge cases"
- **Output**: Comprehensive test suite with temporal/spatial cases
- **Verification**: Manually validated test logic and added assertions

### Documentation
- **Prompt**: "Generate detailed docstrings for conflict detection functions"
- **Output**: Complete function documentation
- **Review**: Ensured accuracy and clarity

### Algorithm Optimization
- **Prompt**: "Optimize point-to-segment distance calculation"
- **Output**: Vectorized NumPy implementation
- **Testing**: Benchmarked against original version

**Key Takeaway**: AI tools significantly accelerated scaffolding and boilerplate generation, but human oversight was critical for correctness, edge cases, and design decisions.

---

## 📝 Assignment Deliverables Checklist

- [x] Modular, well-commented code
- [x] Spatial conflict detection
- [x] Temporal conflict checking  
- [x] Conflict explanation and reporting
- [x] Query interface (CLI and Python API)
- [x] 2D visualization with conflict highlights
- [x] Animated trajectory playback
- [x] Unit tests (trajectory, detector)
- [x] Integration tests (scenarios)
- [x] README with setup and usage
- [x] Reflection document (see `docs/reflection.md`)
- [x] Demo video script (see `demo_video/script.md`)
- [x] **Extra Credit**: 3D support with altitude checking
- [x] **Extra Credit**: AI-assisted development documentation

---

## 📄 License

This project is created for educational purposes as part of the FlytBase Robotics Assignment 2025.

---

## 👨‍💻 Author

**Your Name**  
B.Tech Robotics Engineering  
Submission Date: [DATE]

---

## 🙏 Acknowledgments

- FlytBase for the assignment design
- AI coding assistants (Claude, GitHub Copilot) for development acceleration
- NumPy and Matplotlib communities for excellent documentation

---

## 📞 Support

For questions or issues:
1. Check the documentation in `docs/reflection.md`
2. Review test cases for usage examples
3. Run `python -m src.cli --help` for CLI options
