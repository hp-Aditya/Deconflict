"""
Visualization functions for trajectories and conflicts.
Enhanced with modern aesthetics and interactive features.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle, FancyBboxPatch
from matplotlib import cm
from typing import List, Optional
from .data_models import Flight, Conflict
from .trajectory import interpolate_trajectory, build_segments

# Enhanced color palette with semantic meanings
COLORS = {
    # Primary flight - Trust blue
    'primary': '#2563EB',      # Modern blue - Your mission
    'primary_light': '#60A5FA',
    'primary_path': '#3B82F6',  # Path color
    
    # Simulated flights - Distinct colors for each
    'simulated': '#7C3AED',    # Purple
    'simulated_alt': '#EC4899', # Pink
    'simulated_alt2': '#F59E0B', # Orange
    
    # Status colors - Semantic meanings
    'safe': '#10B981',         # Green - Safe/clear
    'safe_light': '#34D399',
    'warning': '#F59E0B',      # Yellow/Orange - Warning
    'warning_light': '#FCD34D',
    'danger': '#DC2626',       # Red - Conflict/danger
    'danger_light': '#F87171',
    'critical': '#991B1B',     # Dark red - Critical
    
    # Conflict severity levels
    'conflict_low': '#F59E0B',   # Yellow - Low severity
    'conflict_medium': '#F97316', # Orange - Medium severity
    'conflict_high': '#DC2626',   # Red - High severity
    'conflict_critical': '#991B1B', # Dark red - Critical
    
    # Navigation markers
    'start': '#10B981',        # Green - Start point
    'end': '#3B82F6',         # Blue - End point (changed from red)
    'waypoint': '#60A5FA',     # Light blue - Waypoints
    
    # UI elements
    'background': '#FFFFFF',   # White background
    'background_alt': '#F9FAFB', # Light gray for panels
    'grid': '#E5E7EB',         # Grid lines
    'text': '#1F2937',         # Main text
    'text_light': '#6B7280',   # Secondary text
    'border': '#D1D5DB',       # Borders
    
    # Status indicators
    'status_clear': '#10B981',  # Clear status
    'status_warning': '#F59E0B', # Warning status
    'status_conflict': '#DC2626', # Conflict status
}

# Try to import plotly for interactive visualizations
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


def get_conflict_severity(min_distance: float, safety_buffer: float) -> str:
    """
    Determine conflict severity based on distance violation.
    
    Args:
        min_distance: Minimum distance between drones
        safety_buffer: Required safety buffer
        
    Returns:
        Severity level: 'low', 'medium', 'high', or 'critical'
    """
    violation = safety_buffer - min_distance
    violation_percent = (violation / safety_buffer) * 100
    
    if violation_percent < 20:
        return 'low'
    elif violation_percent < 50:
        return 'medium'
    elif violation_percent < 80:
        return 'high'
    else:
        return 'critical'


def get_conflict_color(severity: str) -> str:
    """Get color for conflict based on severity."""
    severity_map = {
        'low': COLORS['conflict_low'],
        'medium': COLORS['conflict_medium'],
        'high': COLORS['conflict_high'],
        'critical': COLORS['conflict_critical']
    }
    return severity_map.get(severity, COLORS['danger'])


def apply_modern_style():
    """Apply modern styling to matplotlib plots."""
    # Try modern seaborn style, fallback to default if not available
    try:
        plt.style.use('seaborn-v0_8-darkgrid')
    except OSError:
        try:
            plt.style.use('seaborn-darkgrid')
        except OSError:
            plt.style.use('default')
    
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'DejaVu Sans', 'Liberation Sans'],
        'font.size': 11,
        'axes.labelsize': 12,
        'axes.titlesize': 14,
        'axes.titleweight': 'bold',
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.titlesize': 16,
        'figure.titleweight': 'bold',
        'grid.alpha': 0.3,
        'axes.grid': True,
        'axes.axisbelow': True,
    })


def plot_2d_trajectories(primary: Flight,
                         simulated_flights: List[Flight],
                         conflicts: Optional[List[Conflict]] = None,
                         safety_buffer: float = 10.0,
                         figsize=(14, 11),
                         style='modern'):
    """
    Plot 2D trajectories with conflict highlights - Enhanced with modern aesthetics.

    Args:
        primary: Primary flight
        simulated_flights: List of simulated flights
        conflicts: List of conflicts (optional)
        safety_buffer: Safety buffer for visualization
        figsize: Figure size
        style: Style theme ('modern' or 'classic')
    """
    if style == 'modern':
        apply_modern_style()
    
    fig, ax = plt.subplots(figsize=figsize, facecolor='white')
    fig.patch.set_facecolor('white')
    ax.set_facecolor(COLORS['background'])

    # Enhanced color palette for simulated flights
    sim_colors = [
        '#7C3AED', '#EC4899', '#F59E0B', '#10B981', 
        '#3B82F6', '#8B5CF6', '#EF4444', '#06B6D4'
    ]
    
    # Plot primary flight with enhanced styling
    times, positions = interpolate_trajectory(primary, dt=0.3)
    ax.plot(positions[:, 0], positions[:, 1], 
            color=COLORS['primary'], linewidth=4, 
            label=f'Primary: {primary.id}', zorder=3,
            alpha=0.9, solid_capstyle='round')
    
    # Add gradient effect to primary path
    for i in range(len(positions) - 1):
        alpha = 0.6 + 0.4 * (i / len(positions))
        ax.plot([positions[i, 0], positions[i+1, 0]], 
                [positions[i, 1], positions[i+1, 1]],
                color=COLORS['primary'], linewidth=4, 
                alpha=alpha, zorder=3)

    # Plot waypoints with modern styling
    wp_x = [wp.x for wp in primary.waypoints]
    wp_y = [wp.y for wp in primary.waypoints]
    ax.scatter(wp_x, wp_y, c=COLORS['primary_light'], 
              s=120, marker='o', zorder=5, edgecolors='white',
              linewidths=2, alpha=0.9, label='Waypoints')

    # Start marker - enhanced
    start_wp = primary.waypoints[0]
    ax.scatter([start_wp.x], [start_wp.y], 
              c=COLORS['start'], s=300, marker='^', 
              label='Start', zorder=6, edgecolors='white',
              linewidths=2.5, alpha=0.95)
    
    # End marker - enhanced
    end_wp = primary.waypoints[-1]
    ax.scatter([end_wp.x], [end_wp.y], 
              c=COLORS['end'], s=300, marker='s', 
              label='End', zorder=6, edgecolors='white',
              linewidths=2.5, alpha=0.95)

    # Plot simulated flights with enhanced styling
    for i, sim_flight in enumerate(simulated_flights):
        times, positions = interpolate_trajectory(sim_flight, dt=0.3)
        color = sim_colors[i % len(sim_colors)]
        
        ax.plot(positions[:, 0], positions[:, 1], 
                '--', color=color, linewidth=2.5, 
                alpha=0.75, label=f'Sim: {sim_flight.id}',
                zorder=2, dash_capstyle='round')

        # Waypoints for simulated flights
        wp_x = [wp.x for wp in sim_flight.waypoints]
        wp_y = [wp.y for wp in sim_flight.waypoints]
        ax.scatter(wp_x, wp_y, c=color, s=80, 
                  marker='o', alpha=0.7, zorder=4,
                  edgecolors='white', linewidths=1.5)

    # Enhanced conflict visualization with severity-based coloring
    if conflicts:
        for idx, conflict in enumerate(conflicts):
            loc = conflict.location
            severity = get_conflict_severity(conflict.min_distance, conflict.safety_buffer)
            conflict_color = get_conflict_color(severity)
            
            # Safety buffer circle with gradient effect
            for radius in [safety_buffer * 0.7, safety_buffer]:
                circle = Circle((loc[0], loc[1]), radius, 
                              color=conflict_color, 
                              fill=False, linewidth=2.5 if radius == safety_buffer else 1.5, 
                              linestyle='--', alpha=0.4 if radius < safety_buffer else 0.7,
                              zorder=8)
                ax.add_patch(circle)
            
            # Conflict marker - enhanced with severity color
            ax.scatter([loc[0]], [loc[1]], 
                      c=conflict_color, s=400, 
                      marker='X', zorder=11, 
                      edgecolors='white', linewidths=3,
                      alpha=0.95, label=f'Conflict ({severity})' if idx == 0 else '')

            # Enhanced annotation with better styling
            violation = conflict.safety_buffer - conflict.min_distance
            ax.annotate(
                f'⚠ CONFLICT #{idx+1}\n'
                f'Time: {conflict.time:.1f}s\n'
                f'Distance: {conflict.min_distance:.2f}m\n'
                f'Violation: {violation:.2f}m',
                xy=(loc[0], loc[1]), 
                xytext=(15, 15),
                textcoords='offset points', 
                fontsize=10,
                fontweight='bold',
                bbox=dict(
                    boxstyle='round,pad=0.8', 
                    facecolor='#FEF3C7', 
                    edgecolor=COLORS['conflict'],
                    linewidth=2,
                    alpha=0.95
                ),
                arrowprops=dict(
                    arrowstyle='->', 
                    connectionstyle='arc3,rad=0.2',
                    color=COLORS['conflict'],
                    lw=2
                ),
                zorder=12
            )

    # Enhanced axis styling
    ax.set_xlabel('X Position (meters)', fontsize=13, fontweight='600', color=COLORS['text'])
    ax.set_ylabel('Y Position (meters)', fontsize=13, fontweight='600', color=COLORS['text'])
    ax.set_title('UAV Strategic Deconfliction Analysis', 
                fontsize=16, fontweight='bold', pad=20, color=COLORS['text'])
    
    # Enhanced legend
    legend = ax.legend(loc='upper left', fontsize=10, framealpha=0.95,
                      fancybox=True, shadow=True, edgecolor=COLORS['grid'])
    legend.get_frame().set_facecolor('white')
    
    # Enhanced grid
    ax.grid(True, alpha=0.4, color=COLORS['grid'], linestyle='-', linewidth=0.8)
    ax.set_aspect('equal', adjustable='box')
    
    # Add subtle border
    for spine in ax.spines.values():
        spine.set_edgecolor(COLORS['grid'])
        spine.set_linewidth(1.5)

    plt.tight_layout()
    return fig, ax


def animate_2d_trajectories(primary: Flight,
                            simulated_flights: List[Flight],
                            conflicts: Optional[List[Conflict]] = None,
                            safety_buffer: float = 10.0,
                            dt: float = 0.1,
                            figsize=(14, 11)):
    """
    Create animated visualization of drone trajectories - Enhanced with modern aesthetics.

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
    apply_modern_style()
    fig, ax = plt.subplots(figsize=figsize, facecolor='white')
    fig.patch.set_facecolor('white')
    ax.set_facecolor(COLORS['background'])

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

    # Enhanced color palette
    sim_colors = [
        '#7C3AED', '#EC4899', '#F59E0B', '#10B981', 
        '#3B82F6', '#8B5CF6', '#EF4444', '#06B6D4'
    ]
    
    # Plot static elements (waypoints, paths) with enhanced styling
    for wp in primary.waypoints:
        ax.plot(wp.x, wp.y, 'o', color=COLORS['primary_light'], 
               markersize=8, alpha=0.4, zorder=1)

    for i, (times, positions, _) in enumerate(sim_trajectories):
        color = sim_colors[i % len(sim_colors)]
        ax.plot(positions[:, 0], positions[:, 1], '--', 
                color=color, linewidth=2, alpha=0.4, zorder=1)

    ax.plot(primary_pos[:, 0], primary_pos[:, 1], '-', 
            color=COLORS['primary'], linewidth=2.5, alpha=0.4, zorder=1)

    # Initialize moving elements with enhanced styling
    primary_point, = ax.plot([], [], 'o', color=COLORS['primary'], 
                            markersize=16, zorder=12, label='Primary',
                            markeredgecolor='white', markeredgewidth=2.5)
    primary_buffer = Circle((0, 0), safety_buffer, color=COLORS['primary'], 
                           fill=True, linewidth=2.5, alpha=0.15, zorder=8)
    primary_buffer_outline = Circle((0, 0), safety_buffer, color=COLORS['primary'], 
                                    fill=False, linewidth=2, alpha=0.6, linestyle='--', zorder=9)
    ax.add_patch(primary_buffer)
    ax.add_patch(primary_buffer_outline)

    sim_points = []
    sim_buffers = []
    sim_buffers_outline = []
    for i in range(len(sim_trajectories)):
        color = sim_colors[i % len(sim_colors)]
        point, = ax.plot([], [], 'o', color=color, 
                        markersize=14, zorder=11, label=f'Sim {i+1}',
                        markeredgecolor='white', markeredgewidth=2)
        sim_points.append(point)

        buffer_circle = Circle((0, 0), safety_buffer, color=color,
                             fill=True, linewidth=2, alpha=0.12, zorder=7)
        buffer_outline = Circle((0, 0), safety_buffer, color=color,
                               fill=False, linewidth=1.5, alpha=0.5, 
                               linestyle='--', zorder=8)
        ax.add_patch(buffer_circle)
        ax.add_patch(buffer_outline)
        sim_buffers.append(buffer_circle)
        sim_buffers_outline.append(buffer_outline)

    # Enhanced time display
    time_text = ax.text(0.02, 0.98, '', transform=ax.transAxes,
                       fontsize=15, fontweight='bold', verticalalignment='top',
                       bbox=dict(boxstyle='round,pad=0.8', 
                                facecolor='white', 
                                edgecolor=COLORS['primary'],
                                linewidth=2,
                                alpha=0.95),
                       color=COLORS['text'])

    # Set axis limits
    all_positions = [primary_pos]
    all_positions.extend([traj[1] for traj in sim_trajectories])
    all_x = np.concatenate([pos[:, 0] for pos in all_positions])
    all_y = np.concatenate([pos[:, 1] for pos in all_positions])

    margin = 20
    ax.set_xlim(all_x.min() - margin, all_x.max() + margin)
    ax.set_ylim(all_y.min() - margin, all_y.max() + margin)

    ax.set_xlabel('X Position (meters)', fontsize=13, fontweight='600', color=COLORS['text'])
    ax.set_ylabel('Y Position (meters)', fontsize=13, fontweight='600', color=COLORS['text'])
    ax.set_title('UAV Deconfliction - Real-time Animation', 
                fontsize=16, fontweight='bold', pad=20, color=COLORS['text'])
    legend = ax.legend(loc='upper right', fontsize=10, framealpha=0.95,
                      fancybox=True, shadow=True, edgecolor=COLORS['grid'])
    legend.get_frame().set_facecolor('white')
    ax.grid(True, alpha=0.4, color=COLORS['grid'], linestyle='-', linewidth=0.8)
    ax.set_aspect('equal', adjustable='box')
    
    for spine in ax.spines.values():
        spine.set_edgecolor(COLORS['grid'])
        spine.set_linewidth(1.5)

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
            primary_buffer_outline.center = (pos[0], pos[1])
            primary_buffer.set_visible(True)
            primary_buffer_outline.set_visible(True)
        else:
            primary_point.set_data([], [])
            primary_buffer.set_visible(False)
            primary_buffer_outline.set_visible(False)

        # Update simulated drones
        for i, (times, positions, _) in enumerate(sim_trajectories):
            if times[0] <= t <= times[-1]:
                idx = np.argmin(np.abs(times - t))
                pos = positions[idx]
                sim_points[i].set_data([pos[0]], [pos[1]])
                sim_buffers[i].center = (pos[0], pos[1])
                sim_buffers_outline[i].center = (pos[0], pos[1])
                sim_buffers[i].set_visible(True)
                sim_buffers_outline[i].set_visible(True)
            else:
                sim_points[i].set_data([], [])
                sim_buffers[i].set_visible(False)
                sim_buffers_outline[i].set_visible(False)

        time_text.set_text(f'⏱ Time: {t:.2f}s')

        return ([primary_point, primary_buffer, primary_buffer_outline, time_text] + 
                sim_points + sim_buffers + sim_buffers_outline)

    anim = FuncAnimation(fig, animate, init_func=init, 
                        frames=len(anim_times), interval=50, 
                        blit=False, repeat=True)

    return anim


def plot_3d_trajectories(primary: Flight,
                        simulated_flights: List[Flight],
                        conflicts: Optional[List[Conflict]] = None,
                        safety_buffer: float = 10.0,
                        figsize=(16, 12)):
    """
    Plot 3D trajectories with conflict highlights - Enhanced with modern aesthetics.

    Args:
        primary: Primary flight
        simulated_flights: List of simulated flights
        conflicts: List of conflicts (optional)
        safety_buffer: Safety buffer for visualization
        figsize: Figure size
    """
    apply_modern_style()
    fig = plt.figure(figsize=figsize, facecolor='white')
    fig.patch.set_facecolor('white')
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor(COLORS['background'])

    # Enhanced color palette
    sim_colors = [
        '#7C3AED', '#EC4899', '#F59E0B', '#10B981', 
        '#3B82F6', '#8B5CF6', '#EF4444', '#06B6D4'
    ]

    # Plot primary flight with enhanced styling
    times, positions = interpolate_trajectory(primary, dt=0.3)
    ax.plot(positions[:, 0], positions[:, 1], positions[:, 2],
            color=COLORS['primary'], linewidth=4, 
            label=f'Primary: {primary.id}', zorder=3, alpha=0.9)

    # Waypoints with enhanced styling
    wp_pos = np.array([[wp.x, wp.y, wp.z] for wp in primary.waypoints])
    ax.scatter(wp_pos[:, 0], wp_pos[:, 1], wp_pos[:, 2],
              c=COLORS['primary_light'], s=150, marker='o', 
              zorder=5, edgecolors='white', linewidths=2, alpha=0.9)

    # Start and end markers - enhanced
    start_wp = primary.waypoints[0]
    ax.scatter([start_wp.x], [start_wp.y], [start_wp.z], 
              c=COLORS['start'], s=400, marker='^',
              label='Start', zorder=6, edgecolors='white', linewidths=2.5)
    
    end_wp = primary.waypoints[-1]
    ax.scatter([end_wp.x], [end_wp.y], [end_wp.z], 
              c=COLORS['end'], s=400, marker='s',
              label='End', zorder=6, edgecolors='white', linewidths=2.5)

    # Plot simulated flights with enhanced styling
    for i, sim_flight in enumerate(simulated_flights):
        times, positions = interpolate_trajectory(sim_flight, dt=0.3)
        color = sim_colors[i % len(sim_colors)]
        
        ax.plot(positions[:, 0], positions[:, 1], positions[:, 2],
                '--', color=color, linewidth=3, alpha=0.75,
                label=f'Sim: {sim_flight.id}', zorder=2)

        wp_pos = np.array([[wp.x, wp.y, wp.z] for wp in sim_flight.waypoints])
        ax.scatter(wp_pos[:, 0], wp_pos[:, 1], wp_pos[:, 2],
                  c=color, s=100, marker='o', alpha=0.7, 
                  zorder=4, edgecolors='white', linewidths=1.5)

    # Enhanced conflict visualization
    if conflicts:
        for idx, conflict in enumerate(conflicts):
            loc = conflict.location
            z_val = loc[2] if len(loc) > 2 else 0
            
            # Conflict marker
            ax.scatter([loc[0]], [loc[1]], [z_val],
                      c=COLORS['conflict'], s=500, marker='X', 
                      linewidths=4, zorder=10, edgecolors='white',
                      alpha=0.95, label='Conflict' if idx == 0 else '')

    # Enhanced axis styling
    ax.set_xlabel('X Position (meters)', fontsize=13, fontweight='600', 
                 labelpad=10, color=COLORS['text'])
    ax.set_ylabel('Y Position (meters)', fontsize=13, fontweight='600', 
                 labelpad=10, color=COLORS['text'])
    ax.set_zlabel('Altitude (meters)', fontsize=13, fontweight='600', 
                 labelpad=10, color=COLORS['text'])
    ax.set_title('UAV Trajectories - 3D Spatial Analysis', 
                fontsize=16, fontweight='bold', pad=20, color=COLORS['text'])
    
    # Enhanced legend
    legend = ax.legend(loc='upper left', fontsize=10, framealpha=0.95,
                      fancybox=True, shadow=True, edgecolor=COLORS['grid'])
    legend.get_frame().set_facecolor('white')
    
    # Enhanced grid
    ax.grid(True, alpha=0.4, color=COLORS['grid'])

    plt.tight_layout()
    return fig, ax


def save_visualization(fig, filename: str, dpi: int = 150):
    """Save figure to file with enhanced quality."""
    fig.savefig(filename, dpi=dpi, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"✓ Saved visualization to {filename}")


def plot_interactive_2d(primary: Flight,
                       simulated_flights: List[Flight],
                       conflicts: Optional[List[Conflict]] = None,
                       safety_buffer: float = 10.0):
    """
    Create interactive 2D Plotly visualization with hover information.
    
    Args:
        primary: Primary flight
        simulated_flights: List of simulated flights
        conflicts: List of conflicts (optional)
        safety_buffer: Safety buffer for visualization
        
    Returns:
        Plotly figure object
    """
    if not PLOTLY_AVAILABLE:
        print("⚠ Plotly not available. Install with: pip install plotly")
        return None
    
    fig = go.Figure()
    
    # Enhanced color palette
    sim_colors = [
        '#7C3AED', '#EC4899', '#F59E0B', '#10B981', 
        '#3B82F6', '#8B5CF6', '#EF4444', '#06B6D4'
    ]
    
    # Primary flight trajectory
    times, positions = interpolate_trajectory(primary, dt=0.2)
    fig.add_trace(go.Scatter(
        x=positions[:, 0],
        y=positions[:, 1],
        mode='lines+markers',
        name=f'Primary: {primary.id}',
        line=dict(color=COLORS['primary'], width=4),
        marker=dict(size=6, color=COLORS['primary_light']),
        hovertemplate='<b>Primary Flight</b><br>' +
                      'X: %{x:.2f}m<br>' +
                      'Y: %{y:.2f}m<extra></extra>'
    ))
    
    # Primary waypoints
    wp_x = [wp.x for wp in primary.waypoints]
    wp_y = [wp.y for wp in primary.waypoints]
    fig.add_trace(go.Scatter(
        x=wp_x,
        y=wp_y,
        mode='markers',
        name='Waypoints',
        marker=dict(size=12, color=COLORS['primary_light'], 
                   line=dict(width=2, color='white')),
        hovertemplate='<b>Waypoint</b><br>' +
                      'X: %{x:.2f}m<br>' +
                      'Y: %{y:.2f}m<extra></extra>'
    ))
    
    # Start marker
    start_wp = primary.waypoints[0]
    fig.add_trace(go.Scatter(
        x=[start_wp.x],
        y=[start_wp.y],
        mode='markers',
        name='Start',
        marker=dict(size=20, color=COLORS['start'], symbol='triangle-up',
                   line=dict(width=2, color='white')),
        hovertemplate='<b>Start Point</b><br>' +
                      'X: %{x:.2f}m<br>' +
                      'Y: %{y:.2f}m<extra></extra>'
    ))
    
    # End marker
    end_wp = primary.waypoints[-1]
    fig.add_trace(go.Scatter(
        x=[end_wp.x],
        y=[end_wp.y],
        mode='markers',
        name='End',
        marker=dict(size=20, color=COLORS['end'], symbol='square',
                   line=dict(width=2, color='white')),
        hovertemplate='<b>End Point</b><br>' +
                      'X: %{x:.2f}m<br>' +
                      'Y: %{y:.2f}m<extra></extra>'
    ))
    
    # Simulated flights
    for i, sim_flight in enumerate(simulated_flights):
        times, positions = interpolate_trajectory(sim_flight, dt=0.2)
        color = sim_colors[i % len(sim_colors)]
        
        fig.add_trace(go.Scatter(
            x=positions[:, 0],
            y=positions[:, 1],
            mode='lines+markers',
            name=f'Sim: {sim_flight.id}',
            line=dict(color=color, width=3, dash='dash'),
            marker=dict(size=5, color=color),
            hovertemplate=f'<b>{sim_flight.id}</b><br>' +
                          'X: %{x:.2f}m<br>' +
                          'Y: %{y:.2f}m<extra></extra>'
        ))
    
    # Conflicts
    if conflicts:
        for idx, conflict in enumerate(conflicts):
            loc = conflict.location
            violation = conflict.safety_buffer - conflict.min_distance
            
            # Safety buffer circle
            theta = np.linspace(0, 2*np.pi, 50)
            circle_x = loc[0] + safety_buffer * np.cos(theta)
            circle_y = loc[1] + safety_buffer * np.sin(theta)
            
            fig.add_trace(go.Scatter(
                x=circle_x,
                y=circle_y,
                mode='lines',
                name=f'Buffer #{idx+1}',
                line=dict(color=COLORS['conflict'], width=2, dash='dot'),
                showlegend=False,
                hoverinfo='skip'
            ))
            
            # Conflict marker
            fig.add_trace(go.Scatter(
                x=[loc[0]],
                y=[loc[1]],
                mode='markers',
                name=f'Conflict #{idx+1}',
                marker=dict(size=25, color=COLORS['conflict'], symbol='x',
                          line=dict(width=3, color='white')),
                hovertemplate=f'<b>⚠ CONFLICT #{idx+1}</b><br>' +
                             f'Time: {conflict.time:.2f}s<br>' +
                             f'Distance: {conflict.min_distance:.2f}m<br>' +
                             f'Violation: {violation:.2f}m<extra></extra>'
            ))
    
    # Layout
    fig.update_layout(
        title=dict(
            text='UAV Strategic Deconfliction - Interactive Analysis',
            font=dict(size=20, color=COLORS['text'])
        ),
        xaxis=dict(
            title='X Position (meters)',
            titlefont=dict(size=14, color=COLORS['text']),
            gridcolor=COLORS['grid'],
            showgrid=True
        ),
        yaxis=dict(
            title='Y Position (meters)',
            titlefont=dict(size=14, color=COLORS['text']),
            gridcolor=COLORS['grid'],
            showgrid=True,
            scaleanchor='x',
            scaleratio=1
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode='closest',
        legend=dict(
            bgcolor='white',
            bordercolor=COLORS['grid'],
            borderwidth=1
        ),
        width=1200,
        height=900
    )
    
    return fig


def plot_4d_time_slider(primary: Flight,
                       simulated_flights: List[Flight],
                       conflicts: Optional[List[Conflict]] = None,
                       safety_buffer: float = 10.0,
                       dt: float = 0.5):
    """
    Create 4D visualization (3D space + time) with interactive time slider.
    Extra credit feature.
    
    Args:
        primary: Primary flight
        simulated_flights: List of simulated flights
        conflicts: List of conflicts (optional)
        safety_buffer: Safety buffer for visualization
        dt: Time step for animation
        
    Returns:
        Plotly figure object with time slider
    """
    if not PLOTLY_AVAILABLE:
        print("⚠ Plotly not available. Install with: pip install plotly")
        return None
    
    # Interpolate trajectories
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
    
    # Create time frames
    time_frames = np.arange(t_min, t_max + dt, dt)
    
    sim_colors = [
        '#7C3AED', '#EC4899', '#F59E0B', '#10B981', 
        '#3B82F6', '#8B5CF6', '#EF4444', '#06B6D4'
    ]
    
    frames = []
    for t in time_frames:
        frame_data = []
        
        # Primary drone at time t
        if primary_times[0] <= t <= primary_times[-1]:
            idx = np.argmin(np.abs(primary_times - t))
            pos = primary_pos[idx]
            frame_data.append(go.Scatter3d(
                x=[pos[0]],
                y=[pos[1]],
                z=[pos[2] if len(pos) > 2 else 0],
                mode='markers',
                marker=dict(size=15, color=COLORS['primary'], symbol='circle'),
                name='Primary',
                showlegend=False
            ))
        
        # Simulated drones at time t
        for i, (times, positions, _) in enumerate(sim_trajectories):
            if times[0] <= t <= times[-1]:
                idx = np.argmin(np.abs(times - t))
                pos = positions[idx]
                color = sim_colors[i % len(sim_colors)]
                frame_data.append(go.Scatter3d(
                    x=[pos[0]],
                    y=[pos[1]],
                    z=[pos[2] if len(pos) > 2 else 0],
                    mode='markers',
                    marker=dict(size=12, color=color, symbol='circle'),
                    name=f'Sim {i+1}',
                    showlegend=False
                ))
        
        frames.append(go.Frame(data=frame_data, name=f"{t:.1f}"))
    
    # Base traces (full trajectories)
    data = []
    
    # Primary trajectory
    data.append(go.Scatter3d(
        x=primary_pos[:, 0],
        y=primary_pos[:, 1],
        z=primary_pos[:, 2] if primary_pos.shape[1] > 2 else np.zeros(len(primary_pos)),
        mode='lines',
        name=f'Primary: {primary.id}',
        line=dict(color=COLORS['primary'], width=4),
        showlegend=True
    ))
    
    # Simulated trajectories
    for i, (times, positions, flight_id) in enumerate(sim_trajectories):
        color = sim_colors[i % len(sim_colors)]
        z_vals = positions[:, 2] if positions.shape[1] > 2 else np.zeros(len(positions))
        data.append(go.Scatter3d(
            x=positions[:, 0],
            y=positions[:, 1],
            z=z_vals,
            mode='lines',
            name=f'Sim: {flight_id}',
            line=dict(color=color, width=3, dash='dash'),
            showlegend=True
        ))
    
    # Create figure
    fig = go.Figure(
        data=data,
        frames=frames
    )
    
    # Add play button and slider
    fig.update_layout(
        title=dict(
            text='UAV Deconfliction - 4D Spatio-Temporal Analysis',
            font=dict(size=20, color=COLORS['text'])
        ),
        scene=dict(
            xaxis_title='X Position (meters)',
            yaxis_title='Y Position (meters)',
            zaxis_title='Altitude (meters)',
            bgcolor='white',
            gridcolor=COLORS['grid']
        ),
        updatemenus=[{
            'type': 'buttons',
            'showactive': False,
            'buttons': [
                {
                    'label': '▶ Play',
                    'method': 'animate',
                    'args': [None, {
                        'frame': {'duration': 100, 'redraw': True},
                        'fromcurrent': True,
                        'transition': {'duration': 50}
                    }]
                },
                {
                    'label': '⏸ Pause',
                    'method': 'animate',
                    'args': [[None], {
                        'frame': {'duration': 0, 'redraw': False},
                        'mode': 'immediate',
                        'transition': {'duration': 0}
                    }]
                }
            ]
        }],
        sliders=[{
            'active': 0,
            'currentvalue': {
                'prefix': 'Time: ',
                'suffix': 's',
                'xanchor': 'left'
            },
            'steps': [
                {
                    'args': [[frame.name], {
                        'frame': {'duration': 0, 'redraw': True},
                        'mode': 'immediate',
                        'transition': {'duration': 0}
                    }],
                    'label': f'{t:.1f}s',
                    'method': 'animate'
                }
                for t, frame in zip(time_frames, frames)
            ]
        }],
        width=1400,
        height=900
    )
    
    return fig


def create_interactive_dashboard(primary: Flight,
                                 simulated_flights: List[Flight],
                                 conflicts: Optional[List[Conflict]] = None,
                                 safety_buffer: float = 10.0,
                                 initial_time: Optional[float] = None):
    """
    Create an interactive dashboard with manual controls for deconfliction analysis.
    
    Features:
    - Real-time safety buffer adjustment
    - Time scrubbing with slider
    - Status indicators
    - Conflict severity visualization
    - Manual control panel
    
    Args:
        primary: Primary flight
        simulated_flights: List of simulated flights
        conflicts: List of conflicts (optional)
        safety_buffer: Initial safety buffer
        initial_time: Initial time for visualization
        
    Returns:
        Plotly figure object with interactive controls
    """
    if not PLOTLY_AVAILABLE:
        print("⚠ Plotly not available. Install with: pip install plotly")
        return None
    
    # Determine time range
    t_min = min(primary.t_start, min(f.t_start for f in simulated_flights))
    t_max = max(primary.t_end, max(f.t_end for f in simulated_flights))
    
    if initial_time is None:
        initial_time = (t_min + t_max) / 2
    
    # Create subplots: main plot + status panel
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Flight Trajectories', 'Status Dashboard', 
                       'Conflict Timeline', 'Control Panel'),
        specs=[[{"colspan": 2}, None],
               [{"type": "xy"}, {"type": "table"}]],
        row_heights=[0.7, 0.3],
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    # Enhanced color palette
    sim_colors = [
        COLORS['simulated'], COLORS['simulated_alt'], COLORS['simulated_alt2'],
        '#10B981', '#3B82F6', '#8B5CF6', '#EF4444', '#06B6D4'
    ]
    
    # Plot primary flight
    times, positions = interpolate_trajectory(primary, dt=0.2)
    fig.add_trace(go.Scatter(
        x=positions[:, 0],
        y=positions[:, 1],
        mode='lines+markers',
        name=f'🛸 Primary: {primary.id}',
        line=dict(color=COLORS['primary'], width=5),
        marker=dict(size=8, color=COLORS['primary_light']),
        hovertemplate='<b>Primary Flight</b><br>' +
                      'X: %{x:.2f}m<br>' +
                      'Y: %{y:.2f}m<br>' +
                      '<extra></extra>',
        showlegend=True
    ), row=1, col=1)
    
    # Plot simulated flights
    for i, sim_flight in enumerate(simulated_flights):
        times, positions = interpolate_trajectory(sim_flight, dt=0.2)
        color = sim_colors[i % len(sim_colors)]
        
        fig.add_trace(go.Scatter(
            x=positions[:, 0],
            y=positions[:, 1],
            mode='lines+markers',
            name=f'✈ Sim: {sim_flight.id}',
            line=dict(color=color, width=3, dash='dash'),
            marker=dict(size=6, color=color),
            hovertemplate=f'<b>{sim_flight.id}</b><br>' +
                          'X: %{x:.2f}m<br>' +
                          'Y: %{y:.2f}m<br>' +
                          '<extra></extra>',
            showlegend=True
        ), row=1, col=1)
    
    # Plot conflicts with severity coloring
    if conflicts:
        for idx, conflict in enumerate(conflicts):
            loc = conflict.location
            severity = get_conflict_severity(conflict.min_distance, conflict.safety_buffer)
            conflict_color = get_conflict_color(severity)
            violation = conflict.safety_buffer - conflict.min_distance
            
            # Safety buffer circle
            theta = np.linspace(0, 2*np.pi, 50)
            circle_x = loc[0] + safety_buffer * np.cos(theta)
            circle_y = loc[1] + safety_buffer * np.sin(theta)
            
            fig.add_trace(go.Scatter(
                x=circle_x,
                y=circle_y,
                mode='lines',
                name=f'Buffer #{idx+1}',
                line=dict(color=conflict_color, width=2, dash='dot'),
                showlegend=False,
                hoverinfo='skip'
            ), row=1, col=1)
            
            # Conflict marker
            severity_emoji = {'low': '⚠️', 'medium': '🔶', 'high': '🔴', 'critical': '🚨'}
            fig.add_trace(go.Scatter(
                x=[loc[0]],
                y=[loc[1]],
                mode='markers+text',
                name=f'{severity_emoji.get(severity, "⚠")} Conflict #{idx+1}',
                marker=dict(size=30, color=conflict_color, symbol='x',
                          line=dict(width=3, color='white')),
                text=[f'#{idx+1}'],
                textposition='middle center',
                textfont=dict(size=14, color='white', family='Arial Black'),
                hovertemplate=f'<b>{severity_emoji.get(severity, "⚠")} CONFLICT #{idx+1}</b><br>' +
                             f'Severity: {severity.upper()}<br>' +
                             f'Time: {conflict.time:.2f}s<br>' +
                             f'Distance: {conflict.min_distance:.2f}m<br>' +
                             f'Violation: {violation:.2f}m<br>' +
                             f'Buffer: {conflict.safety_buffer:.2f}m<extra></extra>',
                showlegend=True
            ), row=1, col=1)
    
    # Status Dashboard (row 2, col 1)
    status_color = COLORS['status_clear'] if not conflicts else COLORS['status_conflict']
    status_text = "✅ CLEAR" if not conflicts else f"❌ {len(conflicts)} CONFLICT(S)"
    
    fig.add_trace(go.Scatter(
        x=[0, 1],
        y=[0.5, 0.5],
        mode='markers+text',
        marker=dict(size=200, color=status_color, symbol='circle'),
        text=[status_text],
        textposition='middle center',
        textfont=dict(size=24, color='white', family='Arial Black'),
        showlegend=False,
        hoverinfo='skip'
    ), row=2, col=1)
    
    # Add status details
    if conflicts:
        for idx, conflict in enumerate(conflicts):
            severity = get_conflict_severity(conflict.min_distance, conflict.safety_buffer)
            fig.add_trace(go.Scatter(
                x=[0.2 + idx * 0.15],
                y=[0.3],
                mode='markers+text',
                marker=dict(size=100, color=get_conflict_color(severity), symbol='circle'),
                text=[f'#{idx+1}<br>{severity.upper()}'],
                textposition='middle center',
                textfont=dict(size=12, color='white'),
                showlegend=False,
                hovertemplate=f'Conflict #{idx+1}: {severity}<extra></extra>'
            ), row=2, col=1)
    
    # Conflict Timeline (row 2, col 2) - Table
    if conflicts:
        conflict_data = []
        for idx, conflict in enumerate(conflicts, 1):
            severity = get_conflict_severity(conflict.min_distance, conflict.safety_buffer)
            violation = conflict.safety_buffer - conflict.min_distance
            conflict_data.append([
                f"#{idx}",
                f"{conflict.time:.1f}s",
                f"{conflict.min_distance:.2f}m",
                f"{violation:.2f}m",
                severity.upper(),
                conflict.conflicting_flight_id
            ])
        
        fig.add_trace(go.Table(
            header=dict(
                values=['ID', 'Time', 'Distance', 'Violation', 'Severity', 'Conflicting Flight'],
                fill_color=COLORS['background_alt'],
                font=dict(size=12, color=COLORS['text']),
                align='center'
            ),
            cells=dict(
                values=list(zip(*conflict_data)),
                fill_color=[['white', COLORS['background_alt']] * len(conflict_data)],
                font=dict(size=11, color=COLORS['text']),
                align='center'
            )
        ), row=2, col=2)
    else:
        fig.add_trace(go.Table(
            header=dict(
                values=['Status'],
                fill_color=COLORS['safe'],
                font=dict(size=14, color='white'),
                align='center'
            ),
            cells=dict(
                values=[['✅ No Conflicts Detected']],
                fill_color=[[COLORS['safe_light']]],
                font=dict(size=12, color=COLORS['text']),
                align='center'
            )
        ), row=2, col=2)
    
    # Update layout
    fig.update_layout(
        title=dict(
            text='🎮 Interactive Deconfliction Dashboard - Manual Control Panel',
            font=dict(size=22, color=COLORS['text'], family='Arial Black'),
            x=0.5
        ),
        height=1000,
        showlegend=True,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Arial', size=11, color=COLORS['text'])
    )
    
    # Update axes
    fig.update_xaxes(
        title_text='X Position (meters)',
        titlefont=dict(size=14, color=COLORS['text']),
        gridcolor=COLORS['grid'],
        showgrid=True,
        row=1, col=1
    )
    
    fig.update_yaxes(
        title_text='Y Position (meters)',
        titlefont=dict(size=14, color=COLORS['text']),
        gridcolor=COLORS['grid'],
        showgrid=True,
        scaleanchor='x',
        scaleratio=1,
        row=1, col=1
    )
    
    # Status dashboard axes
    fig.update_xaxes(
        range=[-0.1, 1.1],
        showgrid=False,
        showticklabels=False,
        zeroline=False,
        row=2, col=1
    )
    
    fig.update_yaxes(
        range=[0, 1],
        showgrid=False,
        showticklabels=False,
        zeroline=False,
        row=2, col=1
    )
    
    # Add annotations for manual controls
    fig.add_annotation(
        text="💡 <b>Manual Controls:</b><br>" +
             "• Adjust safety buffer in code<br>" +
             "• Use Plotly zoom/pan tools<br>" +
             "• Hover for details<br>" +
             "• Click legend to toggle flights",
        xref="paper", yref="paper",
        x=1.02, y=0.5,
        xanchor="left", yanchor="middle",
        showarrow=False,
        bgcolor=COLORS['background_alt'],
        bordercolor=COLORS['border'],
        borderwidth=2,
        font=dict(size=10, color=COLORS['text'])
    )
    
    return fig
