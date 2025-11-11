
# Create example_scenarios.py - Test scenarios
example_scenarios_content = '''"""
Example test scenarios for deconfliction system.
"""
from .data_models import Flight, Waypoint


def scenario_no_conflict() -> tuple:
    """
    Scenario with no conflicts - drones are well separated.
    """
    primary = Flight(
        id="PRIMARY_01",
        waypoints=[
            Waypoint(0, 0),
            Waypoint(50, 50),
            Waypoint(100, 50),
            Waypoint(100, 0)
        ],
        t_start=0.0,
        t_end=60.0,
        speed=5.0
    )
    
    simulated = [
        Flight(
            id="SIM_01",
            waypoints=[
                Waypoint(0, 100),
                Waypoint(50, 150),
                Waypoint(100, 150)
            ],
            t_start=0.0,
            t_end=50.0,
            speed=5.0
        ),
        Flight(
            id="SIM_02",
            waypoints=[
                Waypoint(150, 0),
                Waypoint(150, 100),
                Waypoint(200, 100)
            ],
            t_start=10.0,
            t_end=70.0,
            speed=5.0
        )
    ]
    
    return primary, simulated


def scenario_spatial_conflict() -> tuple:
    """
    Scenario with spatial conflict - paths cross.
    """
    primary = Flight(
        id="PRIMARY_02",
        waypoints=[
            Waypoint(0, 50),
            Waypoint(100, 50)
        ],
        t_start=0.0,
        t_end=40.0,
        speed=5.0
    )
    
    simulated = [
        Flight(
            id="SIM_03",
            waypoints=[
                Waypoint(50, 0),
                Waypoint(50, 100)
            ],
            t_start=5.0,
            t_end=45.0,
            speed=5.0
        )
    ]
    
    return primary, simulated


def scenario_temporal_safe() -> tuple:
    """
    Scenario where paths cross but timing prevents conflict.
    """
    primary = Flight(
        id="PRIMARY_03",
        waypoints=[
            Waypoint(0, 50),
            Waypoint(100, 50)
        ],
        t_start=0.0,
        t_end=30.0,
        speed=5.0
    )
    
    simulated = [
        Flight(
            id="SIM_04",
            waypoints=[
                Waypoint(50, 0),
                Waypoint(50, 100)
            ],
            t_start=40.0,  # Starts after primary finishes
            t_end=70.0,
            speed=5.0
        )
    ]
    
    return primary, simulated


def scenario_multiple_conflicts() -> tuple:
    """
    Scenario with multiple conflicts from different drones.
    """
    primary = Flight(
        id="PRIMARY_04",
        waypoints=[
            Waypoint(50, 0),
            Waypoint(50, 50),
            Waypoint(50, 100),
            Waypoint(100, 100)
        ],
        t_start=0.0,
        t_end=80.0,
        speed=5.0
    )
    
    simulated = [
        Flight(
            id="SIM_05",
            waypoints=[
                Waypoint(0, 50),
                Waypoint(100, 50)
            ],
            t_start=10.0,
            t_end=50.0,
            speed=5.0
        ),
        Flight(
            id="SIM_06",
            waypoints=[
                Waypoint(50, 80),
                Waypoint(50, 120)
            ],
            t_start=40.0,
            t_end=80.0,
            speed=5.0
        )
    ]
    
    return primary, simulated


def scenario_3d_altitude_separation() -> tuple:
    """
    3D scenario where altitude provides separation.
    Extra credit scenario.
    """
    primary = Flight(
        id="PRIMARY_3D_01",
        waypoints=[
            Waypoint(0, 0, 50),
            Waypoint(100, 100, 50)
        ],
        t_start=0.0,
        t_end=50.0,
        speed=5.0
    )
    
    simulated = [
        Flight(
            id="SIM_3D_01",
            waypoints=[
                Waypoint(0, 100, 100),  # Higher altitude
                Waypoint(100, 0, 100)
            ],
            t_start=0.0,
            t_end=50.0,
            speed=5.0
        )
    ]
    
    return primary, simulated


def scenario_3d_conflict() -> tuple:
    """
    3D scenario with actual conflict at same altitude.
    Extra credit scenario.
    """
    primary = Flight(
        id="PRIMARY_3D_02",
        waypoints=[
            Waypoint(0, 50, 75),
            Waypoint(100, 50, 75)
        ],
        t_start=0.0,
        t_end=40.0,
        speed=5.0
    )
    
    simulated = [
        Flight(
            id="SIM_3D_02",
            waypoints=[
                Waypoint(50, 0, 75),  # Same altitude, crossing path
                Waypoint(50, 100, 75)
            ],
            t_start=5.0,
            t_end=45.0,
            speed=5.0
        )
    ]
    
    return primary, simulated


def get_all_scenarios() -> dict:
    """
    Get all test scenarios.
    
    Returns:
        Dictionary mapping scenario names to (primary, simulated) tuples
    """
    return {
        "no_conflict": scenario_no_conflict(),
        "spatial_conflict": scenario_spatial_conflict(),
        "temporal_safe": scenario_temporal_safe(),
        "multiple_conflicts": scenario_multiple_conflicts(),
        "3d_altitude_separation": scenario_3d_altitude_separation(),
        "3d_conflict": scenario_3d_conflict()
    }
'''

with open("deconflict/src/example_scenarios.py", "w") as f:
    f.write(example_scenarios_content)

print("✓ Created example_scenarios.py")
