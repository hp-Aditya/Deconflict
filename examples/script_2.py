
# Create trajectory.py - Trajectory interpolation and segment building
trajectory_content = '''"""
Trajectory interpolation and segment generation.
"""
import numpy as np
from typing import List
from .data_models import Flight, Segment, Waypoint


def compute_segment_times(flight: Flight) -> List[float]:
    """
    Compute time allocation for each segment based on path length.
    Distributes total mission time proportionally to segment lengths.
    
    Args:
        flight: Flight object with waypoints and time window
    
    Returns:
        List of timestamps for each waypoint (including start and end)
    """
    n_waypoints = len(flight.waypoints)
    
    # Calculate segment lengths
    lengths = []
    for i in range(n_waypoints - 1):
        start = flight.waypoints[i].to_array(flight.is_3d())
        end = flight.waypoints[i + 1].to_array(flight.is_3d())
        length = np.linalg.norm(end - start)
        lengths.append(length)
    
    total_length = sum(lengths)
    
    if total_length == 0:
        # All waypoints are at same location - distribute time evenly
        return np.linspace(flight.t_start, flight.t_end, n_waypoints).tolist()
    
    # Allocate time proportionally to distance
    times = [flight.t_start]
    cumulative_time = flight.t_start
    total_duration = flight.t_end - flight.t_start
    
    for length in lengths[:-1]:
        time_for_segment = (length / total_length) * total_duration
        cumulative_time += time_for_segment
        times.append(cumulative_time)
    
    times.append(flight.t_end)  # Ensure exact end time
    
    return times


def build_segments(flight: Flight) -> List[Segment]:
    """
    Build list of flight segments from waypoints with time allocation.
    
    Args:
        flight: Flight object
    
    Returns:
        List of Segment objects
    """
    times = compute_segment_times(flight)
    segments = []
    
    for i in range(len(flight.waypoints) - 1):
        segment = Segment(
            start=flight.waypoints[i],
            end=flight.waypoints[i + 1],
            t_start=times[i],
            t_end=times[i + 1],
            flight_id=flight.id
        )
        segments.append(segment)
    
    return segments


def interpolate_trajectory(flight: Flight, dt: float = 0.1) -> tuple:
    """
    Interpolate full trajectory at regular time intervals.
    
    Args:
        flight: Flight object
        dt: Time step for interpolation (seconds)
    
    Returns:
        Tuple of (times, positions) where:
            times: np.ndarray of shape (N,)
            positions: np.ndarray of shape (N, 2) or (N, 3)
    """
    segments = build_segments(flight)
    is_3d = flight.is_3d()
    
    times = []
    positions = []
    
    for segment in segments:
        # Generate time samples for this segment
        t_samples = np.arange(segment.t_start, segment.t_end, dt)
        if len(t_samples) == 0 or t_samples[-1] < segment.t_end - dt/2:
            t_samples = np.append(t_samples, segment.t_end)
        
        for t in t_samples:
            times.append(t)
            pos = segment.position_at_time(t, include_z=is_3d)
            positions.append(pos)
    
    return np.array(times), np.array(positions)


def get_velocity_vector(segment: Segment, include_z: bool = False) -> np.ndarray:
    """
    Compute velocity vector for a segment.
    
    Args:
        segment: Segment object
        include_z: Include z-component
    
    Returns:
        Velocity vector as numpy array
    """
    if segment.duration() == 0:
        return np.zeros(3 if include_z else 2)
    
    start_pos = segment.start.to_array(include_z)
    end_pos = segment.end.to_array(include_z)
    
    displacement = end_pos - start_pos
    velocity = displacement / segment.duration()
    
    return velocity


def get_speed(segment: Segment, include_z: bool = False) -> float:
    """
    Compute speed (magnitude of velocity) for a segment.
    
    Args:
        segment: Segment object
        include_z: Include z-component
    
    Returns:
        Speed in m/s
    """
    velocity = get_velocity_vector(segment, include_z)
    return np.linalg.norm(velocity)
'''

with open("deconflict/src/trajectory.py", "w") as f:
    f.write(trajectory_content)

print("✓ Created trajectory.py")
