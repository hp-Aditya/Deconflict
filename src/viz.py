"""
Visualization functions for trajectories and conflicts.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle
from mpl_toolkits.mplot3d import Axes3D
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
            ax.annotate(f't={conflict.time:.1f}s\n{conflict.min_distance:.1f}m',
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
              color='blue', s=100, marker='o', zorder=4)

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


def animate_3d_trajectories(primary: Flight,
                            simulated_flights: List[Flight],
                            conflicts: Optional[List[Conflict]] = None,
                            safety_buffer: float = 10.0,
                            dt: float = 0.1,
                            figsize=(14, 10),
                            fps: int = 20):
    """
    Create animated 3D visualization of drone trajectories with time domain.
    
    Args:
        primary: Primary flight
        simulated_flights: List of simulated flights
        conflicts: List of conflicts (optional)
        safety_buffer: Safety buffer radius for visualization
        dt: Time step for animation
        figsize: Figure size
        fps: Frames per second for animation
        
    Returns:
        FuncAnimation object
    """
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection='3d')
    
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
    
    # Plot static trajectory paths (faded)
    ax.plot(primary_pos[:, 0], primary_pos[:, 1], primary_pos[:, 2],
            'b-', linewidth=1.5, alpha=0.2, label='Primary Path')
    
    # Waypoints for primary
    wp_pos = np.array([[wp.x, wp.y, wp.z] for wp in primary.waypoints])
    ax.scatter(wp_pos[:, 0], wp_pos[:, 1], wp_pos[:, 2],
              c='blue', s=60, marker='o', alpha=0.4, zorder=2)
    
    # Colors for simulated drones
    colors = plt.cm.Set3(np.linspace(0, 1, len(simulated_flights)))
    
    # Plot simulated paths
    for i, (times, positions, drone_id) in enumerate(sim_trajectories):
        ax.plot(positions[:, 0], positions[:, 1], positions[:, 2],
                '--', color=colors[i], linewidth=1.5, alpha=0.2,
                label=f'{drone_id} Path')
        
        # Get waypoints from the flight object
        sim_flight = simulated_flights[i]
        wp_pos = np.array([[wp.x, wp.y, wp.z] for wp in sim_flight.waypoints])
        ax.scatter(wp_pos[:, 0], wp_pos[:, 1], wp_pos[:, 2],
                  c=colors[i], s=40, marker='o', alpha=0.4, zorder=2)
    
    # Initialize moving elements
    # Primary drone
    primary_point, = ax.plot([], [], [], 'bo', markersize=14, 
                            markeredgecolor='darkblue', markeredgewidth=2,
                            label='Primary Drone', zorder=10)
    primary_trail, = ax.plot([], [], [], 'b-', linewidth=3, alpha=0.7, zorder=9)
    
    # Safety sphere for primary (represented by wire frame)
    primary_sphere = None
    
    # Simulated drones
    sim_points = []
    sim_trails = []
    sim_spheres = []
    
    for i, color in enumerate(colors):
        point, = ax.plot([], [], [], 'o', color=color, markersize=12,
                        markeredgecolor='black', markeredgewidth=1.5,
                        label=f'Sim Drone {i+1}', zorder=10)
        sim_points.append(point)
        
        trail, = ax.plot([], [], [], color=color, linewidth=2.5, 
                        alpha=0.6, zorder=9)
        sim_trails.append(trail)
        
        sim_spheres.append(None)
    
    # Conflict markers
    conflict_markers = []
    if conflicts:
        for conflict in conflicts:
            loc = conflict.location
            z_val = loc[2] if len(loc) > 2 else 0
            marker, = ax.plot([loc[0]], [loc[1]], [z_val], 
                            'rx', markersize=20, markeredgewidth=4,
                            alpha=0, zorder=15)
            conflict_markers.append((marker, conflict))
    
    # Time display
    time_text = ax.text2D(0.02, 0.98, '', transform=ax.transAxes,
                         fontsize=16, verticalalignment='top', fontweight='bold',
                         bbox=dict(boxstyle='round,pad=0.7', 
                                  facecolor='lightblue', alpha=0.9,
                                  edgecolor='navy', linewidth=2))
    
    # Status display
    status_text = ax.text2D(0.02, 0.90, '', transform=ax.transAxes,
                           fontsize=12, verticalalignment='top',
                           bbox=dict(boxstyle='round,pad=0.5', 
                                    facecolor='wheat', alpha=0.85))
    
    # Set axis limits with margin
    all_positions = [primary_pos]
    all_positions.extend([traj[1] for traj in sim_trajectories])
    all_x = np.concatenate([pos[:, 0] for pos in all_positions])
    all_y = np.concatenate([pos[:, 1] for pos in all_positions])
    all_z = np.concatenate([pos[:, 2] for pos in all_positions])
    
    margin = safety_buffer * 2
    ax.set_xlim(all_x.min() - margin, all_x.max() + margin)
    ax.set_ylim(all_y.min() - margin, all_y.max() + margin)
    ax.set_zlim(max(0, all_z.min() - margin), all_z.max() + margin)
    
    ax.set_xlabel('X (meters)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Y (meters)', fontsize=12, fontweight='bold')
    ax.set_zlabel('Altitude (meters)', fontsize=12, fontweight='bold')
    ax.set_title('3D UAV Trajectory Animation - Time Domain', 
                fontsize=16, fontweight='bold', pad=20)
    
    ax.legend(loc='upper right', fontsize=9, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Set initial view angle
    ax.view_init(elev=25, azim=45)
    
    def create_sphere_wireframe(center, radius, color, alpha=0.15):
        """Create a wireframe sphere for safety buffer visualization."""
        u = np.linspace(0, 2 * np.pi, 15)
        v = np.linspace(0, np.pi, 10)
        x = center[0] + radius * np.outer(np.cos(u), np.sin(v))
        y = center[1] + radius * np.outer(np.sin(u), np.sin(v))
        z = center[2] + radius * np.outer(np.ones(np.size(u)), np.cos(v))
        return ax.plot_surface(x, y, z, color=color, alpha=alpha, 
                              edgecolor='none', shade=True)
    
    def init():
        """Initialize animation."""
        primary_point.set_data([], [])
        primary_point.set_3d_properties([])
        primary_trail.set_data([], [])
        primary_trail.set_3d_properties([])
        
        for point, trail in zip(sim_points, sim_trails):
            point.set_data([], [])
            point.set_3d_properties([])
            trail.set_data([], [])
            trail.set_3d_properties([])
        
        time_text.set_text('')
        status_text.set_text('')
        
        return [primary_point, primary_trail, time_text, status_text] + \
               sim_points + sim_trails
    
    def animate(frame):
        """Update animation frame."""
        nonlocal primary_sphere
        t = anim_times[frame]
        
        active_drones = 0
        conflict_now = False
        
        # Update primary drone
        if primary_times[0] <= t <= primary_times[-1]:
            idx = np.argmin(np.abs(primary_times - t))
            pos = primary_pos[idx]
            
            # Update position marker
            primary_point.set_data([pos[0]], [pos[1]])
            primary_point.set_3d_properties([pos[2]])
            
            # Update trail (show last N points)
            trail_length = min(30, idx + 1)
            trail_start = max(0, idx - trail_length + 1)
            trail_pos = primary_pos[trail_start:idx+1]
            primary_trail.set_data(trail_pos[:, 0], trail_pos[:, 1])
            primary_trail.set_3d_properties(trail_pos[:, 2])
            
            # Update safety sphere
            if primary_sphere:
                primary_sphere.remove()
            primary_sphere = create_sphere_wireframe(pos, safety_buffer, 
                                                    'blue', alpha=0.1)
            
            active_drones += 1
        else:
            primary_point.set_data([], [])
            primary_point.set_3d_properties([])
            primary_trail.set_data([], [])
            primary_trail.set_3d_properties([])
            if primary_sphere:
                primary_sphere.remove()
                primary_sphere = None
        
        # Update simulated drones
        for i, (times, positions, _) in enumerate(sim_trajectories):
            if times[0] <= t <= times[-1]:
                idx = np.argmin(np.abs(times - t))
                pos = positions[idx]
                
                # Update position
                sim_points[i].set_data([pos[0]], [pos[1]])
                sim_points[i].set_3d_properties([pos[2]])
                
                # Update trail
                trail_length = min(30, idx + 1)
                trail_start = max(0, idx - trail_length + 1)
                trail_pos = positions[trail_start:idx+1]
                sim_trails[i].set_data(trail_pos[:, 0], trail_pos[:, 1])
                sim_trails[i].set_3d_properties(trail_pos[:, 2])
                
                # Update safety sphere
                if sim_spheres[i]:
                    sim_spheres[i].remove()
                sim_spheres[i] = create_sphere_wireframe(pos, safety_buffer,
                                                        colors[i], alpha=0.08)
                
                active_drones += 1
            else:
                sim_points[i].set_data([], [])
                sim_points[i].set_3d_properties([])
                sim_trails[i].set_data([], [])
                sim_trails[i].set_3d_properties([])
                if sim_spheres[i]:
                    sim_spheres[i].remove()
                    sim_spheres[i] = None
        
        # Check for active conflicts at current time
        for marker, conflict in conflict_markers:
            if abs(conflict.time - t) < dt * 2:  # Within time window
                marker.set_alpha(1.0)
                conflict_now = True
            else:
                marker.set_alpha(0.3)
        
        # Update time display
        time_text.set_text(f'Time: {t:.2f}s / {t_max:.2f}s')
        
        # Update status
        status_info = f'Active Drones: {active_drones}'
        if conflict_now:
            status_info += '\n⚠️  CONFLICT DETECTED!'
            time_text.set_bbox(dict(boxstyle='round,pad=0.7', 
                                   facecolor='red', alpha=0.95,
                                   edgecolor='darkred', linewidth=2))
            time_text.set_color('white')
            status_text.set_bbox(dict(boxstyle='round,pad=0.5',
                                     facecolor='red', alpha=0.85))
        else:
            status_info += '\n✓ Clear'
            time_text.set_bbox(dict(boxstyle='round,pad=0.7', 
                                   facecolor='lightblue', alpha=0.9,
                                   edgecolor='navy', linewidth=2))
            time_text.set_color('black')
            status_text.set_bbox(dict(boxstyle='round,pad=0.5',
                                     facecolor='lightgreen', alpha=0.85))
        
        status_text.set_text(status_info)
        
        # Rotate view slowly for better 3D perception
        ax.view_init(elev=25, azim=45 + frame * 0.3)
        
        return [primary_point, primary_trail, time_text, status_text] + \
               sim_points + sim_trails + [m for m, _ in conflict_markers]
    
    # Create animation
    anim = FuncAnimation(fig, animate, init_func=init, 
                        frames=len(anim_times), 
                        interval=1000/fps, 
                        blit=False, 
                        repeat=True)
    
    plt.tight_layout()
    return anim


def save_visualization(fig, filename: str, dpi: int = 150):
    """Save figure to file."""
    fig.savefig(filename, dpi=dpi, bbox_inches='tight')
    print(f"Saved visualization to {filename}")