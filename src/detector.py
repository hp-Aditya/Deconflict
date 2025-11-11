"""
Collision detection and conflict checking logic.
"""
import numpy as np
from typing import List, Optional, Tuple
from .data_models import Flight, Segment, Conflict
from .trajectory import build_segments


def time_windows_overlap(t1_start: float, t1_end: float, 
                         t2_start: float, t2_end: float) -> bool:
    """
    Check if two time windows overlap.

    Args:
        t1_start, t1_end: First time window
        t2_start, t2_end: Second time window

    Returns:
        True if windows overlap
    """
    return not (t1_end < t2_start or t2_end < t1_start)


def compute_overlap_window(t1_start: float, t1_end: float,
                           t2_start: float, t2_end: float) -> Optional[Tuple[float, float]]:
    """
    Compute overlapping time window between two intervals.

    Returns:
        (overlap_start, overlap_end) or None if no overlap
    """
    if not time_windows_overlap(t1_start, t1_end, t2_start, t2_end):
        return None

    overlap_start = max(t1_start, t2_start)
    overlap_end = min(t1_end, t2_end)

    return (overlap_start, overlap_end)


def point_to_segment_distance(point: np.ndarray, 
                               seg_start: np.ndarray, 
                               seg_end: np.ndarray) -> float:
    """
    Compute minimum distance from point to line segment.

    Args:
        point: Point coordinates
        seg_start: Segment start coordinates
        seg_end: Segment end coordinates

    Returns:
        Minimum distance
    """
    # Vector from start to end
    segment_vec = seg_end - seg_start
    segment_length_sq = np.dot(segment_vec, segment_vec)

    if segment_length_sq == 0:
        # Segment is a point
        return np.linalg.norm(point - seg_start)

    # Project point onto line (parameter t in [0, 1] for segment)
    t = np.dot(point - seg_start, segment_vec) / segment_length_sq
    t = np.clip(t, 0, 1)

    # Closest point on segment
    closest = seg_start + t * segment_vec

    return np.linalg.norm(point - closest)


def segment_to_segment_distance(seg1: Segment, seg2: Segment, 
                                include_z: bool = False) -> float:
    """
    Compute minimum distance between two line segments (static geometry).
    This is a simplified version - for moving segments, use temporal checks.

    Args:
        seg1, seg2: Segment objects
        include_z: Include z-coordinate

    Returns:
        Minimum distance between segments
    """
    p1_start = seg1.start.to_array(include_z)
    p1_end = seg1.end.to_array(include_z)
    p2_start = seg2.start.to_array(include_z)
    p2_end = seg2.end.to_array(include_z)

    # Compute distances from endpoints to opposite segment
    distances = [
        point_to_segment_distance(p1_start, p2_start, p2_end),
        point_to_segment_distance(p1_end, p2_start, p2_end),
        point_to_segment_distance(p2_start, p1_start, p1_end),
        point_to_segment_distance(p2_end, p1_start, p1_end),
    ]

    return min(distances)


def segment_conflict(seg1: Segment, seg2: Segment, 
                    safety_buffer: float,
                    include_z: bool = False,
                    time_samples: int = 20) -> Optional[Conflict]:
    """
    Check for spatio-temporal conflict between two segments.

    Strategy:
    1. Check if time windows overlap
    2. If yes, sample positions during overlap and check distances
    3. Report conflict if minimum distance < safety_buffer

    Args:
        seg1: Primary flight segment
        seg2: Other flight segment
        safety_buffer: Minimum safe distance (meters)
        include_z: Include altitude in calculations
        time_samples: Number of time samples for checking

    Returns:
        Conflict object if conflict detected, None otherwise
    """
    # Check temporal overlap
    overlap = compute_overlap_window(seg1.t_start, seg1.t_end,
                                     seg2.t_start, seg2.t_end)

    if overlap is None:
        return None  # No temporal overlap

    overlap_start, overlap_end = overlap

    # Sample positions during overlap window
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
            conflict_location = pos1  # Use primary drone location

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


def check_mission(primary: Flight, 
                 simulated_flights: List[Flight],
                 safety_buffer: float = 10.0,
                 include_z: bool = False) -> Tuple[bool, List[Conflict]]:
    """
    Main deconfliction check function.

    Args:
        primary: Primary drone mission to check
        simulated_flights: List of other drone missions
        safety_buffer: Minimum safe distance in meters
        include_z: Perform 3D checks (if False, only 2D)

    Returns:
        Tuple of (is_clear, conflicts):
            is_clear: True if no conflicts detected
            conflicts: List of Conflict objects (empty if clear)
    """
    # Build segments for primary flight
    primary_segments = build_segments(primary)

    all_conflicts = []

    # Check against each simulated flight
    for sim_flight in simulated_flights:
        sim_segments = build_segments(sim_flight)

        # Check each pair of segments
        for p_seg in primary_segments:
            for s_seg in sim_segments:
                conflict = segment_conflict(
                    p_seg, s_seg,
                    safety_buffer=safety_buffer,
                    include_z=include_z
                )

                if conflict is not None:
                    all_conflicts.append(conflict)

    is_clear = len(all_conflicts) == 0

    return is_clear, all_conflicts


def generate_conflict_report(conflicts: List[Conflict]) -> str:
    """
    Generate human-readable conflict report.

    Args:
        conflicts: List of detected conflicts

    Returns:
        Formatted string report
    """
    if not conflicts:
        return "✓ Mission is CLEAR - No conflicts detected."

    report = f"✗ CONFLICTS DETECTED: {len(conflicts)} conflict(s) found\n\n"

    for i, conflict in enumerate(conflicts, 1):
        report += f"Conflict #{i}:\n"
        report += f"  Primary Flight: {conflict.primary_flight_id}\n"
        report += f"  Conflicting Flight: {conflict.conflicting_flight_id}\n"
        report += f"  Time: {conflict.time:.2f}s\n"

        loc_str = ", ".join(f"{c:.2f}" for c in conflict.location)
        report += f"  Location: ({loc_str})\n"
        report += f"  Distance: {conflict.min_distance:.2f}m "
        report += f"(< {conflict.safety_buffer:.2f}m buffer)\n"
        report += f"  Violation: {conflict.safety_buffer - conflict.min_distance:.2f}m\n\n"

    return report
