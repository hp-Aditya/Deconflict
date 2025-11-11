
# Create viz.py - Visualization functions
viz_content = '''"""
Visualization functions for trajectories and conflicts.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle
from typing import List, Optional
from .data_models import Flight, Conflict
from .trajectory import interpolate_trajectory, build_segments


def plot_2d_trajectories(primary: Flight,
                         simulated_flights: List[Flight],
                         conflicts: Optional[List[Conflict]] = None,
                         safety_buffer: float = 10.0,
                         figsize=(12, 10)):
    """
    Plot 2D trajectories with conflict highlights.
    
    Args:
        primary: Primary flight
        simulated_flights: List of simulated flights
        conflicts: List of conflicts (optional)
        safety_buffer: Safety buffer for visualization
        figsize: Figure size
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot primary flight
    times, positions = interpolate_trajectory(primary, dt=0.5)
    ax.plot(positions[:, 0], positions[:, 1], 'b-', linewidth=3, 
            label=f'Primary: {primary.id}', zorder=3)
    
    # Plot waypoints
    for wp in primary.waypoints:
        ax.plot(wp.x, wp.y, 'bo', markersize=8, zorder=4)
    
    # Start and end markers for primary
    ax.plot(primary.waypoints[0].x, primary.waypoints[0].y, 
            'g^', markersize=15, label='Start', zorder=5)
    ax.plot(primary.waypoints[-1].x, primary.waypoints[-1].y, 
            'rs', markersize=15, label='End', zorder=5)
    
    # Plot simulated flights
    colors = plt.cm.tab10(np.linspace(0, 1, len(simulated_flights)))
    
    for i, sim_flight in enumerate(simulated_flights):
        times, positions = interpolate_trajectory(sim_flight, dt=0.5)
        ax.plot(positions[:, 0], positions[:, 1], '--', 
                color=colors[i], linewidth=2, alpha=0.7,
                label=f'Sim: {sim_flight.id}')
        
        # Waypoints for simulated
        for wp in sim_flight.waypoints:
            ax.plot(wp.x, wp.y, 'o', color=colors[i], 
                   markersize=5, alpha=0.7)
    
    # Plot conflicts
    if conflicts:
        for conflict in conflicts:
            loc = conflict.location
            # Red circle at conflict location
            circle = Circle((loc[0], loc[1]), safety_buffer, 
                          color='red', fill=False, linewidth=2, 
                          linestyle='--', alpha=0.6)
            ax.add_patch(circle)
            ax.plot(loc[0], loc[1], 'rx', markersize=15, 
                   markeredgewidth=3, zorder=10)
            
            # Annotate conflict
            ax.annotate(f't={conflict.time:.1f}s\\n{conflict.min_distance:.1f}m',
                       xy=(loc[0], loc[1]), xytext=(10, 10),
                       textcoords='offset points', fontsize=9,
                       bbox=dict(boxstyle='round,pad=0.5', 
                                facecolor='yellow', alpha=0.7),
                       arrowprops=dict(arrowstyle='->', 
                                     connectionstyle='arc3,rad=0'))
    
    ax.set_xlabel('X (meters)', fontsize=12)
    ax.set_ylabel('Y (meters)', fontsize=12)
    ax.set_title('UAV Trajectories - Deconfliction Check', fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal', adjustable='box')
    
    plt.tight_layout()
    return fig, ax


def animate_2d_trajectories(primary: Flight,
                            simulated_flights: List[Flight],
                            conflicts: Optional[List[Conflict]] = None,
                            safety_buffer: float = 10.0,
                            dt: float = 0.1,
                            figsize=(12, 10)):
    """
    Create animated visualization of drone trajectories.
    
    Args:
        primary: Primary flight
        simulated_flights: List of simulated flights
        conflicts: List of conflicts (optional)
        safety_buffer: Safety buffer radius
        dt: Time step for animation
        figsize: Figure size
    
    Returns:
        FuncAnimation object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Interpolate all trajectories
    primary_times, primary_pos = interpolate_trajectory(primary, dt=dt)
    
    sim_trajectories = []
    for sim_flight in simulated_flights:
        times, positions = interpolate_trajectory(sim_flight, dt=dt)
        sim_trajectories.append((times, positions, sim_flight.id))
    
    # Determine time range
    all_times = [primary_times]
    all_times.extend([traj[0] for traj in sim_trajectories])
    t_min = min(times[0] for times in all_times)
    t_max = max(times[-1] for times in all_times)
    
    # Animation time points
    anim_times = np.arange(t_min, t_max, dt)
    
    # Plot static elements (waypoints, paths)
    for wp in primary.waypoints:
        ax.plot(wp.x, wp.y, 'bo', markersize=6, alpha=0.3)
    
    colors = plt.cm.tab10(np.linspace(0, 1, len(simulated_flights)))
    for i, (times, positions, _) in enumerate(sim_trajectories):
        ax.plot(positions[:, 0], positions[:, 1], '--', 
                color=colors[i], linewidth=1, alpha=0.3)
    
    ax.plot(primary_pos[:, 0], primary_pos[:, 1], 'b-', 
            linewidth=1, alpha=0.3)
    
    # Initialize moving elements
    primary_point, = ax.plot([], [], 'bo', markersize=12, zorder=10, label='Primary')
    primary_buffer = Circle((0, 0), safety_buffer, color='blue', 
                           fill=False, linewidth=2, alpha=0.5)
    ax.add_patch(primary_buffer)
    
    sim_points = []
    sim_buffers = []
    for i in range(len(sim_trajectories)):
        point, = ax.plot([], [], 'o', color=colors[i], 
                        markersize=10, zorder=9, label=f'Sim {i+1}')
        sim_points.append(point)
        
        buffer_circle = Circle((0, 0), safety_buffer, color=colors[i],
                             fill=False, linewidth=1.5, alpha=0.3)
        ax.add_patch(buffer_circle)
        sim_buffers.append(buffer_circle)
    
    time_text = ax.text(0.02, 0.98, '', transform=ax.transAxes,
                       fontsize=14, verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Set axis limits
    all_positions = [primary_pos]
    all_positions.extend([traj[1] for traj in sim_trajectories])
    all_x = np.concatenate([pos[:, 0] for pos in all_positions])
    all_y = np.concatenate([pos[:, 1] for pos in all_positions])
    
    margin = 20
    ax.set_xlim(all_x.min() - margin, all_x.max() + margin)
    ax.set_ylim(all_y.min() - margin, all_y.max() + margin)
    
    ax.set_xlabel('X (meters)', fontsize=12)
    ax.set_ylabel('Y (meters)', fontsize=12)
    ax.set_title('UAV Deconfliction - Animated', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal', adjustable='box')
    
    def init():
        primary_point.set_data([], [])
        for point in sim_points:
            point.set_data([], [])
        time_text.set_text('')
        return [primary_point, time_text] + sim_points
    
    def animate(frame):
        t = anim_times[frame]
        
        # Update primary drone
        if primary_times[0] <= t <= primary_times[-1]:
            idx = np.argmin(np.abs(primary_times - t))
            pos = primary_pos[idx]
            primary_point.set_data([pos[0]], [pos[1]])
            primary_buffer.center = (pos[0], pos[1])
            primary_buffer.set_visible(True)
        else:
            primary_point.set_data([], [])
            primary_buffer.set_visible(False)
        
        # Update simulated drones
        for i, (times, positions, _) in enumerate(sim_trajectories):
            if times[0] <= t <= times[-1]:
                idx = np.argmin(np.abs(times - t))
                pos = positions[idx]
                sim_points[i].set_data([pos[0]], [pos[1]])
                sim_buffers[i].center = (pos[0], pos[1])
                sim_buffers[i].set_visible(True)
            else:
                sim_points[i].set_data([], [])
                sim_buffers[i].set_visible(False)
        
        time_text.set_text(f'Time: {t:.2f}s')
        
        return [primary_point, primary_buffer, time_text] + sim_points + sim_buffers
    
    anim = FuncAnimation(fig, animate, init_func=init, 
                        frames=len(anim_times), interval=50, 
                        blit=False, repeat=True)
    
    return anim


def plot_3d_trajectories(primary: Flight,
                        simulated_flights: List[Flight],
                        conflicts: Optional[List[Conflict]] = None,
                        safety_buffer: float = 10.0,
                        figsize=(14, 10)):
    """
    Plot 3D trajectories with conflict highlights.
    
    Args:
        primary: Primary flight
        simulated_flights: List of simulated flights
        conflicts: List of conflicts (optional)
        safety_buffer: Safety buffer for visualization
        figsize: Figure size
    """
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot primary flight
    times, positions = interpolate_trajectory(primary, dt=0.5)
    ax.plot(positions[:, 0], positions[:, 1], positions[:, 2],
            'b-', linewidth=3, label=f'Primary: {primary.id}', zorder=3)
    
    # Waypoints
    wp_pos = np.array([[wp.x, wp.y, wp.z] for wp in primary.waypoints])
    ax.scatter(wp_pos[:, 0], wp_pos[:, 1], wp_pos[:, 2],
              c='blue', s=100, marker='o', zorder=4)
    
    # Start and end markers
    ax.scatter([primary.waypoints[0].x], [primary.waypoints[0].y], 
              [primary.waypoints[0].z], c='green', s=200, marker='^',
              label='Start', zorder=5)
    ax.scatter([primary.waypoints[-1].x], [primary.waypoints[-1].y],
              [primary.waypoints[-1].z], c='red', s=200, marker='s',
              label='End', zorder=5)
    
    # Plot simulated flights
    colors = plt.cm.tab10(np.linspace(0, 1, len(simulated_flights)))
    
    for i, sim_flight in enumerate(simulated_flights):
        times, positions = interpolate_trajectory(sim_flight, dt=0.5)
        ax.plot(positions[:, 0], positions[:, 1], positions[:, 2],
                '--', color=colors[i], linewidth=2, alpha=0.7,
                label=f'Sim: {sim_flight.id}')
        
        wp_pos = np.array([[wp.x, wp.y, wp.z] for wp in sim_flight.waypoints])
        ax.scatter(wp_pos[:, 0], wp_pos[:, 1], wp_pos[:, 2],
                  c=colors[i], s=50, marker='o', alpha=0.7)
    
    # Plot conflicts
    if conflicts:
        for conflict in conflicts:
            loc = conflict.location
            ax.scatter([loc[0]], [loc[1]], [loc[2] if len(loc) > 2 else 0],
                      c='red', s=300, marker='x', linewidths=3, zorder=10)
    
    ax.set_xlabel('X (meters)', fontsize=12)
    ax.set_ylabel('Y (meters)', fontsize=12)
    ax.set_zlabel('Z (meters)', fontsize=12)
    ax.set_title('UAV Trajectories - 3D View', fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig, ax


def save_visualization(fig, filename: str, dpi: int = 150):
    """Save figure to file."""
    fig.savefig(filename, dpi=dpi, bbox_inches='tight')
    print(f"Saved visualization to {filename}")
'''

with open("deconflict/src/viz.py", "w") as f:
    f.write(viz_content)

print("✓ Created viz.py")
