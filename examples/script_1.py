
# Create data_models.py - Core data structures
data_models_content = '''"""
Data models for drone missions and waypoints.
"""
from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np


@dataclass
class Waypoint:
    """Represents a single waypoint in 2D or 3D space."""
    x: float
    y: float
    z: float = 0.0  # Optional altitude for 3D
    
    def to_array(self, include_z: bool = False) -> np.ndarray:
        """Convert waypoint to numpy array."""
        if include_z:
            return np.array([self.x, self.y, self.z])
        return np.array([self.x, self.y])
    
    def __repr__(self):
        if self.z != 0.0:
            return f"Waypoint({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"
        return f"Waypoint({self.x:.2f}, {self.y:.2f})"


@dataclass
class Flight:
    """Represents a drone flight mission."""
    id: str
    waypoints: List[Waypoint]
    t_start: float  # Mission start time (seconds)
    t_end: float    # Mission end time (seconds)
    speed: float = 5.0  # Default speed in m/s
    
    def __post_init__(self):
        """Validate flight data."""
        if len(self.waypoints) < 2:
            raise ValueError(f"Flight {self.id} must have at least 2 waypoints")
        if self.t_start >= self.t_end:
            raise ValueError(f"Flight {self.id}: t_start must be < t_end")
        if self.speed <= 0:
            raise ValueError(f"Flight {self.id}: speed must be positive")
    
    def duration(self) -> float:
        """Total mission duration."""
        return self.t_end - self.t_start
    
    def is_3d(self) -> bool:
        """Check if this is a 3D mission."""
        return any(wp.z != 0.0 for wp in self.waypoints)


@dataclass
class Segment:
    """Represents a flight segment between two waypoints."""
    start: Waypoint
    end: Waypoint
    t_start: float
    t_end: float
    flight_id: str
    
    def duration(self) -> float:
        """Segment duration."""
        return self.t_end - self.t_start
    
    def length(self, include_z: bool = False) -> float:
        """Euclidean distance between start and end."""
        start_arr = self.start.to_array(include_z)
        end_arr = self.end.to_array(include_z)
        return np.linalg.norm(end_arr - start_arr)
    
    def position_at_time(self, t: float, include_z: bool = False) -> np.ndarray:
        """
        Linear interpolation of position at time t.
        Returns position as numpy array.
        """
        if t < self.t_start or t > self.t_end:
            raise ValueError(f"Time {t} outside segment bounds [{self.t_start}, {self.t_end}]")
        
        if self.t_start == self.t_end:
            return self.start.to_array(include_z)
        
        # Linear interpolation parameter
        alpha = (t - self.t_start) / (self.t_end - self.t_start)
        
        start_pos = self.start.to_array(include_z)
        end_pos = self.end.to_array(include_z)
        
        return start_pos + alpha * (end_pos - start_pos)
    
    def __repr__(self):
        return f"Segment({self.flight_id}: {self.start} -> {self.end}, t=[{self.t_start:.1f}, {self.t_end:.1f}])"


@dataclass
class Conflict:
    """Represents a detected conflict between two flights."""
    primary_flight_id: str
    conflicting_flight_id: str
    location: Tuple[float, ...]  # (x, y) or (x, y, z)
    time: float
    min_distance: float
    safety_buffer: float
    
    def __repr__(self):
        loc_str = ", ".join(f"{c:.2f}" for c in self.location)
        return (f"Conflict({self.primary_flight_id} ↔ {self.conflicting_flight_id} "
                f"at ({loc_str}) @ t={self.time:.1f}s, "
                f"dist={self.min_distance:.2f}m < buffer={self.safety_buffer:.2f}m)")


def load_flight_from_dict(data: dict) -> Flight:
    """Load a Flight object from dictionary."""
    waypoints = [
        Waypoint(wp['x'], wp['y'], wp.get('z', 0.0))
        for wp in data['waypoints']
    ]
    return Flight(
        id=data['id'],
        waypoints=waypoints,
        t_start=data['t_start'],
        t_end=data['t_end'],
        speed=data.get('speed', 5.0)
    )


def save_flight_to_dict(flight: Flight) -> dict:
    """Save a Flight object to dictionary."""
    return {
        'id': flight.id,
        'waypoints': [
            {'x': wp.x, 'y': wp.y, 'z': wp.z}
            for wp in flight.waypoints
        ],
        't_start': flight.t_start,
        't_end': flight.t_end,
        'speed': flight.speed
    }
'''

with open("deconflict/src/data_models.py", "w") as f:
    f.write(data_models_content)

print("✓ Created data_models.py")
