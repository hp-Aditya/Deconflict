"""
UAV Strategic Deconfliction System
FlytBase Robotics Assignment 2025
"""

from .data_models import Flight, Waypoint, Segment, Conflict
from .trajectory import build_segments, interpolate_trajectory
from .detector import check_mission, generate_conflict_report
from .viz import plot_2d_trajectories, plot_3d_trajectories, animate_2d_trajectories
from .example_scenarios import get_all_scenarios

__version__ = "1.0.0"
__all__ = [
    'Flight', 'Waypoint', 'Segment', 'Conflict',
    'build_segments', 'interpolate_trajectory',
    'check_mission', 'generate_conflict_report',
    'plot_2d_trajectories', 'plot_3d_trajectories', 'animate_2d_trajectories',
    'get_all_scenarios'
]
