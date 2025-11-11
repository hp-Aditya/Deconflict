"""
Unit tests for trajectory module.
"""
import unittest
import numpy as np
from src.data_models import Flight, Waypoint
from src.trajectory import build_segments, compute_segment_times, interpolate_trajectory


class TestTrajectory(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        self.simple_flight = Flight(
            id="TEST_01",
            waypoints=[
                Waypoint(0, 0),
                Waypoint(100, 0),
                Waypoint(100, 100)
            ],
            t_start=0.0,
            t_end=60.0,
            speed=5.0
        )

    def test_compute_segment_times(self):
        """Test time allocation for segments."""
        times = compute_segment_times(self.simple_flight)

        self.assertEqual(len(times), 3)  # 3 waypoints = 3 times
        self.assertEqual(times[0], 0.0)
        self.assertEqual(times[-1], 60.0)
        self.assertTrue(all(times[i] <= times[i+1] for i in range(len(times)-1)))

    def test_build_segments(self):
        """Test segment creation."""
        segments = build_segments(self.simple_flight)

        self.assertEqual(len(segments), 2)  # 3 waypoints = 2 segments

        for seg in segments:
            self.assertEqual(seg.flight_id, "TEST_01")
            self.assertLessEqual(seg.t_start, seg.t_end)
            self.assertGreater(seg.length(), 0)

    def test_interpolate_trajectory(self):
        """Test trajectory interpolation."""
        times, positions = interpolate_trajectory(self.simple_flight, dt=1.0)

        self.assertGreater(len(times), 0)
        self.assertEqual(len(times), len(positions))
        self.assertEqual(positions.shape[1], 2)  # 2D positions

        # Check boundary conditions
        self.assertAlmostEqual(times[0], 0.0, places=1)
        self.assertLessEqual(times[-1], 60.0)

    def test_segment_position_at_time(self):
        """Test position interpolation within segment."""
        segments = build_segments(self.simple_flight)
        seg = segments[0]

        # Test start position
        start_pos = seg.position_at_time(seg.t_start)
        np.testing.assert_array_almost_equal(
            start_pos, np.array([0, 0])
        )

        # Test end position
        end_pos = seg.position_at_time(seg.t_end)
        np.testing.assert_array_almost_equal(
            end_pos, np.array([100, 0])
        )

        # Test midpoint
        mid_time = (seg.t_start + seg.t_end) / 2
        mid_pos = seg.position_at_time(mid_time)
        self.assertAlmostEqual(mid_pos[0], 50, places=0)


if __name__ == '__main__':
    unittest.main()
