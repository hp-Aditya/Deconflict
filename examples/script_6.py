
# Create cli.py - Command line interface
cli_content = '''"""
Command-line interface for deconfliction system.
"""
import argparse
import json
import sys
from typing import List
from .data_models import Flight, load_flight_from_dict
from .detector import check_mission, generate_conflict_report
from .viz import plot_2d_trajectories, plot_3d_trajectories, animate_2d_trajectories, save_visualization
from .example_scenarios import get_all_scenarios
import matplotlib.pyplot as plt


def load_flights_from_json(filepath: str) -> tuple:
    """
    Load primary and simulated flights from JSON file.
    
    Expected format:
    {
        "primary": {...},
        "simulated": [...]
    }
    """
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    primary = load_flight_from_dict(data['primary'])
    simulated = [load_flight_from_dict(flight) for flight in data['simulated']]
    
    return primary, simulated


def run_deconfliction_check(primary: Flight, 
                           simulated: List[Flight],
                           safety_buffer: float = 10.0,
                           include_z: bool = False,
                           visualize: bool = True,
                           animate: bool = False,
                           output_file: str = None):
    """
    Run complete deconfliction check with visualization.
    """
    print(f"\\n{'='*60}")
    print("UAV DECONFLICTION CHECK")
    print(f"{'='*60}")
    print(f"Primary Flight: {primary.id}")
    print(f"  Waypoints: {len(primary.waypoints)}")
    print(f"  Time Window: [{primary.t_start:.1f}s, {primary.t_end:.1f}s]")
    print(f"\\nSimulated Flights: {len(simulated)}")
    for sim in simulated:
        print(f"  - {sim.id}: {len(sim.waypoints)} waypoints, "
              f"t=[{sim.t_start:.1f}s, {sim.t_end:.1f}s]")
    print(f"\\nSafety Buffer: {safety_buffer:.1f}m")
    print(f"Check Mode: {'3D' if include_z else '2D'}")
    print(f"{'='*60}\\n")
    
    # Run check
    is_clear, conflicts = check_mission(
        primary, simulated, 
        safety_buffer=safety_buffer,
        include_z=include_z
    )
    
    # Print report
    report = generate_conflict_report(conflicts)
    print(report)
    
    # Visualization
    if visualize:
        print("\\nGenerating visualization...")
        
        if include_z and primary.is_3d():
            fig, ax = plot_3d_trajectories(
                primary, simulated, conflicts, safety_buffer
            )
        else:
            fig, ax = plot_2d_trajectories(
                primary, simulated, conflicts, safety_buffer
            )
        
        if output_file:
            save_visualization(fig, output_file)
        
        if animate and not include_z:
            print("Generating animation...")
            anim = animate_2d_trajectories(
                primary, simulated, conflicts, safety_buffer
            )
            
            if output_file:
                anim_file = output_file.replace('.png', '_animated.gif')
                print(f"Saving animation to {anim_file}...")
                anim.save(anim_file, writer='pillow', fps=20)
        
        plt.show()
    
    return is_clear, conflicts


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='UAV Strategic Deconfliction System',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--scenario',
        type=str,
        help='Use built-in test scenario',
        choices=['no_conflict', 'spatial_conflict', 'temporal_safe', 
                'multiple_conflicts', '3d_altitude_separation', '3d_conflict']
    )
    
    parser.add_argument(
        '--input',
        type=str,
        help='Path to JSON file with flight data'
    )
    
    parser.add_argument(
        '--buffer',
        type=float,
        default=10.0,
        help='Safety buffer distance in meters (default: 10.0)'
    )
    
    parser.add_argument(
        '--3d',
        action='store_true',
        dest='use_3d',
        help='Enable 3D conflict checking'
    )
    
    parser.add_argument(
        '--no-viz',
        action='store_true',
        help='Disable visualization'
    )
    
    parser.add_argument(
        '--animate',
        action='store_true',
        help='Generate animation (2D only)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output file for visualization (PNG)'
    )
    
    args = parser.parse_args()
    
    # Load flights
    if args.scenario:
        scenarios = get_all_scenarios()
        if args.scenario not in scenarios:
            print(f"Error: Unknown scenario '{args.scenario}'")
            sys.exit(1)
        primary, simulated = scenarios[args.scenario]
        print(f"Using scenario: {args.scenario}")
    elif args.input:
        try:
            primary, simulated = load_flights_from_json(args.input)
            print(f"Loaded flights from: {args.input}")
        except Exception as e:
            print(f"Error loading file: {e}")
            sys.exit(1)
    else:
        print("Error: Must specify --scenario or --input")
        parser.print_help()
        sys.exit(1)
    
    # Run check
    is_clear, conflicts = run_deconfliction_check(
        primary=primary,
        simulated=simulated,
        safety_buffer=args.buffer,
        include_z=args.use_3d,
        visualize=not args.no_viz,
        animate=args.animate,
        output_file=args.output
    )
    
    # Exit code
    sys.exit(0 if is_clear else 1)


if __name__ == '__main__':
    main()
'''

with open("deconflict/src/cli.py", "w") as f:
    f.write(cli_content)

print("✓ Created cli.py")
