"""
Integration tests for complete system.
"""
import unittest
from src.data_models import Flight, Waypoint
from src.detector import check_mission
from src.example_scenarios import get_all_scenarios


class TestIntegration(unittest.TestCase):

    def test_all_scenarios(self):
        """Test all built-in scenarios."""
        scenarios = get_all_scenarios()

        # Test each scenario runs without errors
        for name, (primary, simulated) in scenarios.items():
            with self.subTest(scenario=name):
                is_clear, conflicts = check_mission(
                    primary, simulated, 
                    safety_buffer=10.0,
                    include_z=primary.is_3d()
                )

                # Just verify it runs and returns proper types
                self.assertIsInstance(is_clear, bool)
                self.assertIsInstance(conflicts, list)

    def test_no_conflict_scenario(self):
        """Verify no_conflict scenario is actually clear."""
        scenarios = get_all_scenarios()
        primary, simulated = scenarios["no_conflict"]

        is_clear, conflicts = check_mission(primary, simulated, safety_buffer=10.0)

        self.assertTrue(is_clear, "no_conflict scenario should be clear")
        self.assertEqual(len(conflicts), 0)

    def test_spatial_conflict_scenario(self):
        """Verify spatial_conflict scenario detects conflicts."""
        scenarios = get_all_scenarios()
        primary, simulated = scenarios["spatial_conflict"]

        is_clear, conflicts = check_mission(primary, simulated, safety_buffer=10.0)

        self.assertFalse(is_clear, "spatial_conflict scenario should have conflicts")
        self.assertGreater(len(conflicts), 0)

    def test_temporal_safe_scenario(self):
        """Verify temporal_safe scenario is clear due to timing."""
        scenarios = get_all_scenarios()
        primary, simulated = scenarios["temporal_safe"]

        is_clear, conflicts = check_mission(primary, simulated, safety_buffer=10.0)

        self.assertTrue(is_clear, "temporal_safe scenario should be clear")
        self.assertEqual(len(conflicts), 0)

    def test_3d_altitude_separation(self):
        """Verify 3D altitude separation works."""
        scenarios = get_all_scenarios()
        primary, simulated = scenarios["3d_altitude_separation"]

        # 2D check should show conflict
        is_clear_2d, conflicts_2d = check_mission(
            primary, simulated, safety_buffer=10.0, include_z=False
        )

        # 3D check should be clear (altitude separation)
        is_clear_3d, conflicts_3d = check_mission(
            primary, simulated, safety_buffer=10.0, include_z=True
        )

        self.assertTrue(is_clear_3d, "3D check should be clear with altitude separation")

    def test_varying_safety_buffers(self):
        """Test that larger buffers detect more conflicts."""
        primary = Flight(
            id="PRIMARY",
            waypoints=[Waypoint(0, 0), Waypoint(100, 0)],
            t_start=0.0,
            t_end=30.0
        )

        simulated = [
            Flight(
                id="SIM",
                waypoints=[Waypoint(50, 15), Waypoint(50, 20)],
                t_start=10.0,
                t_end=20.0
            )
        ]

        # Small buffer - should be clear
        is_clear_small, _ = check_mission(primary, simulated, safety_buffer=5.0)

        # Large buffer - should conflict
        is_clear_large, _ = check_mission(primary, simulated, safety_buffer=20.0)

        self.assertTrue(is_clear_small)
        self.assertFalse(is_clear_large)


if __name__ == '__main__':
    unittest.main()
