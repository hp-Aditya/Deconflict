
# Now create all the enhanced interactive files

# 1. Enhanced detector with higher accuracy simulation
enhanced_detector_content = '''"""
Enhanced collision detection with improved accuracy simulation.
"""
import numpy as np
from typing import List, Optional, Tuple
from .data_models import Flight, Segment, Conflict
from .trajectory import build_segments


def time_windows_overlap(t1_start: float, t1_end: float, 
                         t2_start: float, t2_end: float) -> bool:
    """Check if two time windows overlap."""
    return not (t1_end < t2_start or t2_end < t1_start)


def compute_overlap_window(t1_start: float, t1_end: float,
                           t2_start: float, t2_end: float) -> Optional[Tuple[float, float]]:
    """Compute overlapping time window between two intervals."""
    if not time_windows_overlap(t1_start, t1_end, t2_start, t2_end):
        return None
    
    overlap_start = max(t1_start, t2_start)
    overlap_end = min(t1_end, t2_end)
    
    return (overlap_start, overlap_end)


def segment_conflict_high_accuracy(seg1: Segment, seg2: Segment, 
                                   safety_buffer: float,
                                   include_z: bool = False,
                                   time_samples: int = 100) -> Optional[Conflict]:
    """
    High-accuracy spatio-temporal conflict detection.
    Uses more samples (default 100) for better precision.
    
    Args:
        seg1: Primary flight segment
        seg2: Other flight segment
        safety_buffer: Minimum safe distance (meters)
        include_z: Include altitude in calculations
        time_samples: Number of time samples (higher = more accurate)
    
    Returns:
        Conflict object if conflict detected, None otherwise
    """
    # Check temporal overlap
    overlap = compute_overlap_window(seg1.t_start, seg1.t_end,
                                     seg2.t_start, seg2.t_end)
    
    if overlap is None:
        return None
    
    overlap_start, overlap_end = overlap
    
    # High-resolution time sampling
    time_points = np.linspace(overlap_start, overlap_end, time_samples)
    
    min_distance = float('inf')
    conflict_time = None
    conflict_location = None
    
    for t in time_points:
        # Get positions at time t
        pos1 = seg1.position_at_time(t, include_z)
        pos2 = seg2.position_at_time(t, include_z)
        
        # Compute distance
        distance = np.linalg.norm(pos1 - pos2)
        
        if distance < min_distance:
            min_distance = distance
            conflict_time = t
            conflict_location = pos1
    
    # Check if conflict exists
    if min_distance < safety_buffer:
        return Conflict(
            primary_flight_id=seg1.flight_id,
            conflicting_flight_id=seg2.flight_id,
            location=tuple(conflict_location),
            time=conflict_time,
            min_distance=min_distance,
            safety_buffer=safety_buffer
        )
    
    return None


def check_mission_high_accuracy(primary: Flight, 
                                simulated_flights: List[Flight],
                                safety_buffer: float = 10.0,
                                include_z: bool = False,
                                time_samples: int = 100) -> Tuple[bool, List[Conflict]]:
    """
    High-accuracy deconfliction check with configurable sampling.
    
    Args:
        primary: Primary drone mission to check
        simulated_flights: List of other drone missions
        safety_buffer: Minimum safe distance in meters
        include_z: Perform 3D checks
        time_samples: Number of time samples per segment pair
    
    Returns:
        Tuple of (is_clear, conflicts)
    """
    primary_segments = build_segments(primary)
    all_conflicts = []
    
    for sim_flight in simulated_flights:
        sim_segments = build_segments(sim_flight)
        
        for p_seg in primary_segments:
            for s_seg in sim_segments:
                conflict = segment_conflict_high_accuracy(
                    p_seg, s_seg,
                    safety_buffer=safety_buffer,
                    include_z=include_z,
                    time_samples=time_samples
                )
                
                if conflict is not None:
                    all_conflicts.append(conflict)
    
    is_clear = len(all_conflicts) == 0
    return is_clear, all_conflicts


def generate_conflict_report(conflicts: List[Conflict]) -> str:
    """Generate human-readable conflict report."""
    if not conflicts:
        return "✓ Mission is CLEAR - No conflicts detected."
    
    report = f"✗ CONFLICTS DETECTED: {len(conflicts)} conflict(s) found\\n\\n"
    
    for i, conflict in enumerate(conflicts, 1):
        report += f"Conflict #{i}:\\n"
        report += f"  Primary Flight: {conflict.primary_flight_id}\\n"
        report += f"  Conflicting Flight: {conflict.conflicting_flight_id}\\n"
        report += f"  Time: {conflict.time:.2f}s\\n"
        
        loc_str = ", ".join(f"{c:.2f}" for c in conflict.location)
        report += f"  Location: ({loc_str})\\n"
        report += f"  Distance: {conflict.min_distance:.2f}m "
        report += f"(< {conflict.safety_buffer:.2f}m buffer)\\n"
        report += f"  Violation: {conflict.safety_buffer - conflict.min_distance:.2f}m\\n\\n"
    
    return report


# Backward compatibility - default accuracy mode
def segment_conflict(seg1: Segment, seg2: Segment, 
                    safety_buffer: float,
                    include_z: bool = False,
                    time_samples: int = 20) -> Optional[Conflict]:
    """Standard accuracy conflict detection (backward compatible)."""
    return segment_conflict_high_accuracy(
        seg1, seg2, safety_buffer, include_z, time_samples
    )


def check_mission(primary: Flight, 
                 simulated_flights: List[Flight],
                 safety_buffer: float = 10.0,
                 include_z: bool = False) -> Tuple[bool, List[Conflict]]:
    """Standard accuracy mission check (backward compatible)."""
    return check_mission_high_accuracy(
        primary, simulated_flights, safety_buffer, include_z, time_samples=20
    )
'''

# Save the enhanced detector
with open("deconflict/src/detector_enhanced.py", "w") as f:
    f.write(enhanced_detector_content)

print("✓ Created detector_enhanced.py with high-accuracy simulation")
