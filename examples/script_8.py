
# Create test_detector.py
test_detector_content = '''"""
Unit tests for detector module.
"""
import unittest
from src.data_models import Flight, Waypoint
from src.detector import (
    time_windows_overlap, compute_overlap_window,
    segment_conflict, check_mission
)
from src.trajectory import build_segments


class TestDetector(unittest.TestCase):
    
    def test_time_windows_overlap(self):
        """Test time window overlap detection."""
        # Overlapping windows
        self.assertTrue(time_windows_overlap(0, 10, 5, 15))
        self.assertTrue(time_windows_overlap(5, 15, 0, 10))
        self.assertTrue(time_windows_overlap(0, 10, 0, 10))
        
        # Non-overlapping windows
        self.assertFalse(time_windows_overlap(0, 10, 11, 20))
        self.assertFalse(time_windows_overlap(11, 20, 0, 10))
    
    def test_compute_overlap_window(self):
        """Test overlap window computation."""
        # Test overlap
        overlap = compute_overlap_window(0, 10, 5, 15)
        self.assertIsNotNone(overlap)
        self.assertEqual(overlap, (5, 10))
        
        # Test no overlap
        overlap = compute_overlap_window(0, 10, 20, 30)
        self.assertIsNone(overlap)
    
    def test_segment_conflict_no_temporal_overlap(self):
        """Test that segments with no temporal overlap don't conflict."""
        flight1 = Flight(
            id="F1",
            waypoints=[Waypoint(0, 0), Waypoint(100, 0)],
            t_start=0.0,
            t_end=10.0
        )
        
        flight2 = Flight(
            id="F2",
            waypoints=[Waypoint(50, -5), Waypoint(50, 5)],
            t_start=20.0,  # No temporal overlap
            t_end=30.0
        )
        
        seg1 = build_segments(flight1)[0]
        seg2 = build_segments(flight2)[0]
        
        conflict = segment_conflict(seg1, seg2, safety_buffer=10.0)
        self.assertIsNone(conflict)
    
    def test_segment_conflict_spatial_only(self):
        """Test conflict detection when paths are close spatially and temporally."""
        flight1 = Flight(
            id="F1",
            waypoints=[Waypoint(0, 0), Waypoint(100, 0)],
            t_start=0.0,
            t_end=20.0
        )
        
        flight2 = Flight(
            id="F2",
            waypoints=[Waypoint(50, -5), Waypoint(50, 5)],
            t_start=5.0,  # Temporal overlap
            t_end=25.0
        )
        
        seg1 = build_segments(flight1)[0]
        seg2 = build_segments(flight2)[0]
        
        # Should detect conflict with small buffer
        conflict = segment_conflict(seg1, seg2, safety_buffer=10.0)
        self.assertIsNotNone(conflict)
        self.assertEqual(conflict.primary_flight_id, "F1")
        self.assertEqual(conflict.conflicting_flight_id, "F2")
    
    def test_check_mission_no_conflict(self):
        """Test mission check with no conflicts."""
        primary = Flight(
            id="PRIMARY",
            waypoints=[Waypoint(0, 0), Waypoint(100, 0)],
            t_start=0.0,
            t_end=30.0
        )
        
        simulated = [
            Flight(
                id="SIM1",
                waypoints=[Waypoint(0, 100), Waypoint(100, 100)],
                t_start=0.0,
                t_end=30.0
            )
        ]
        
        is_clear, conflicts = check_mission(primary, simulated, safety_buffer=10.0)
        
        self.assertTrue(is_clear)
        self.assertEqual(len(conflicts), 0)
    
    def test_check_mission_with_conflict(self):
        """Test mission check with conflicts."""
        primary = Flight(
            id="PRIMARY",
            waypoints=[Waypoint(0, 50), Waypoint(100, 50)],
            t_start=0.0,
            t_end=40.0
        )
        
        simulated = [
            Flight(
                id="SIM1",
                waypoints=[Waypoint(50, 0), Waypoint(50, 100)],
                t_start=5.0,
                t_end=45.0
            )
        ]
        
        is_clear, conflicts = check_mission(primary, simulated, safety_buffer=10.0)
        
        self.assertFalse(is_clear)
        self.assertGreater(len(conflicts), 0)


if __name__ == '__main__':
    unittest.main()
'''

with open("deconflict/tests/test_detector.py", "w") as f:
    f.write(test_detector_content)

print("✓ Created test_detector.py")
