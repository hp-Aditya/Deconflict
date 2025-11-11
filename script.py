
# Create enhanced interactive version with user inputs

# 1. Create interactive CLI with rich user inputs
interactive_cli_content = '''"""
Interactive command-line interface with user input capabilities.
"""
import argparse
import json
import sys
from typing import List, Tuple
from .data_models import Flight, Waypoint, load_flight_from_dict
from .detector import check_mission, generate_conflict_report
from .viz import plot_2d_trajectories, plot_3d_trajectories, animate_2d_trajectories, save_visualization
from .example_scenarios import get_all_scenarios
import matplotlib.pyplot as plt


def get_user_input_waypoints(drone_id: str, is_3d: bool = False) -> List[Waypoint]:
    """
    Interactively get waypoints from user.
    
    Args:
        drone_id: Identifier for the drone
        is_3d: Whether to ask for z-coordinates
    
    Returns:
        List of Waypoint objects
    """
    print(f"\\n{'='*60}")
    print(f"Enter waypoints for {drone_id}")
    print(f"{'='*60}")
    
    waypoints = []
    waypoint_num = 1
    
    while True:
        print(f"\\nWaypoint #{waypoint_num}:")
        
        try:
            x = float(input(f"  X coordinate (meters): "))
            y = float(input(f"  Y coordinate (meters): "))
            
            if is_3d:
                z = float(input(f"  Z coordinate (altitude in meters): "))
            else:
                z = 0.0
            
            waypoints.append(Waypoint(x, y, z))
            
            if waypoint_num >= 2:  # At least 2 waypoints required
                continue_input = input(f"\\n  Add another waypoint? (y/n): ").lower()
                if continue_input != 'y':
                    break
            
            waypoint_num += 1
            
        except ValueError:
            print("  ❌ Invalid input! Please enter numeric values.")
            continue
        except KeyboardInterrupt:
            print("\\n  ⚠️  Input cancelled.")
            sys.exit(0)
    
    return waypoints


def get_user_input_flight(flight_id: str, is_3d: bool = False) -> Flight:
    """
    Interactively create a Flight from user input.
    
    Args:
        flight_id: Identifier for the flight
        is_3d: Whether this is a 3D flight
    
    Returns:
        Flight object
    """
    print(f"\\n{'='*60}")
    print(f"Configure Flight: {flight_id}")
    print(f"{'='*60}")
    
    # Get waypoints
    waypoints = get_user_input_waypoints(flight_id, is_3d)
    
    # Get timing
    print(f"\\nTiming Configuration:")
    while True:
        try:
            t_start = float(input(f"  Start time (seconds, default 0.0): ") or "0.0")
            t_end = float(input(f"  End time (seconds): "))
            
            if t_end <= t_start:
                print("  ❌ End time must be greater than start time!")
                continue
            
            break
        except ValueError:
            print("  ❌ Invalid input! Please enter numeric values.")
    
    # Get speed (optional)
    while True:
        try:
            speed_input = input(f"  Speed (m/s, default 5.0): ") or "5.0"
            speed = float(speed_input)
            
            if speed <= 0:
                print("  ❌ Speed must be positive!")
                continue
            
            break
        except ValueError:
            print("  ❌ Invalid input! Please enter numeric value.")
    
    return Flight(
        id=flight_id,
        waypoints=waypoints,
        t_start=t_start,
        t_end=t_end,
        speed=speed
    )


def interactive_mode():
    """
    Full interactive mode for creating and testing missions.
    """
    print("\\n" + "="*70)
    print("🚁 UAV DECONFLICTION SYSTEM - INTERACTIVE MODE")
    print("="*70)
    
    # Choose 2D or 3D
    print("\\nChoose flight mode:")
    print("  1. 2D (X, Y coordinates only)")
    print("  2. 3D (X, Y, Z coordinates with altitude)")
    
    while True:
        mode_choice = input("\\nEnter choice (1 or 2): ").strip()
        if mode_choice in ['1', '2']:
            is_3d = (mode_choice == '2')
            break
        print("❌ Invalid choice! Please enter 1 or 2.")
    
    mode_str = "3D" if is_3d else "2D"
    print(f"\\n✓ Selected: {mode_str} mode")
    
    # Create primary flight
    print("\\n" + "="*70)
    print("STEP 1: Create Primary Drone Mission")
    print("="*70)
    primary = get_user_input_flight("PRIMARY", is_3d)
    print(f"\\n✓ Primary flight created with {len(primary.waypoints)} waypoints")
    
    # Create simulated flights
    print("\\n" + "="*70)
    print("STEP 2: Create Simulated Drone Flights")
    print("="*70)
    
    while True:
        try:
            num_sim = int(input("\\nHow many simulated drones? (1-10): "))
            if 1 <= num_sim <= 10:
                break
            print("❌ Please enter a number between 1 and 10.")
        except ValueError:
            print("❌ Invalid input! Please enter a number.")
    
    simulated = []
    for i in range(num_sim):
        print(f"\\n--- Simulated Drone {i+1}/{num_sim} ---")
        sim_flight = get_user_input_flight(f"SIM_{i+1:02d}", is_3d)
        simulated.append(sim_flight)
        print(f"✓ Simulated flight {i+1} created")
    
    # Configure safety buffer
    print("\\n" + "="*70)
    print("STEP 3: Configure Safety Parameters")
    print("="*70)
    
    while True:
        try:
            buffer_input = input("\\nSafety buffer distance (meters, default 10.0): ") or "10.0"
            safety_buffer = float(buffer_input)
            
            if safety_buffer <= 0:
                print("❌ Safety buffer must be positive!")
                continue
            
            break
        except ValueError:
            print("❌ Invalid input! Please enter numeric value.")
    
    # Configure visualization
    print("\\n" + "="*70)
    print("STEP 4: Visualization Options")
    print("="*70)
    
    print("\\nSelect visualization types:")
    print("  1. Static plot only")
    print("  2. Static plot + Animation")
    print("  3. No visualization (report only)")
    
    while True:
        viz_choice = input("\\nEnter choice (1-3): ").strip()
        if viz_choice in ['1', '2', '3']:
            break
        print("❌ Invalid choice! Please enter 1, 2, or 3.")
    
    show_viz = viz_choice != '3'
    show_anim = viz_choice == '2'
    
    # Ask about saving
    save_output = input("\\nSave visualization to file? (y/n): ").lower() == 'y'
    output_file = None
    
    if save_output:
        output_file = input("Enter filename (default: deconfliction_result.png): ").strip()
        if not output_file:
            output_file = "deconfliction_result.png"
        if not output_file.endswith('.png'):
            output_file += '.png'
    
    # Run deconfliction check
    print("\\n" + "="*70)
    print("STEP 5: Running Deconfliction Analysis...")
    print("="*70)
    
    print(f"\\n📊 Configuration Summary:")
    print(f"  Mode: {mode_str}")
    print(f"  Primary flight: {len(primary.waypoints)} waypoints, "
          f"t=[{primary.t_start:.1f}s - {primary.t_end:.1f}s]")
    print(f"  Simulated flights: {len(simulated)}")
    print(f"  Safety buffer: {safety_buffer:.1f}m")
    
    # Perform check
    is_clear, conflicts = check_mission(
        primary, simulated,
        safety_buffer=safety_buffer,
        include_z=is_3d
    )
    
    # Display results
    print("\\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    report = generate_conflict_report(conflicts)
    print(f"\\n{report}")
    
    if not is_clear:
        print(f"\\n⚠️  WARNING: {len(conflicts)} conflict(s) detected!")
        print("Mission is NOT safe to execute.")
    else:
        print("\\n✅ Mission is SAFE to execute!")
    
    # Visualization
    if show_viz:
        print("\\n" + "="*70)
        print("Generating Visualization...")
        print("="*70)
        
        if is_3d:
            fig, ax = plot_3d_trajectories(
                primary, simulated, conflicts, safety_buffer
            )
        else:
            fig, ax = plot_2d_trajectories(
                primary, simulated, conflicts, safety_buffer
            )
        
        if output_file:
            save_visualization(fig, output_file)
        
        if show_anim and not is_3d:
            print("\\nGenerating animation...")
            anim = animate_2d_trajectories(
                primary, simulated, conflicts, safety_buffer
            )
            
            if output_file:
                anim_file = output_file.replace('.png', '_animated.gif')
                print(f"Saving animation to {anim_file}...")
                try:
                    anim.save(anim_file, writer='pillow', fps=20)
                    print(f"✓ Animation saved to {anim_file}")
                except Exception as e:
                    print(f"⚠️  Could not save animation: {e}")
        
        plt.show()
    
    # Save mission data
    save_data = input("\\nSave mission data to JSON file? (y/n): ").lower() == 'y'
    
    if save_data:
        data_file = input("Enter filename (default: mission_data.json): ").strip()
        if not data_file:
            data_file = "mission_data.json"
        if not data_file.endswith('.json'):
            data_file += '.json'
        
        from .data_models import save_flight_to_dict
        
        mission_data = {
            "primary": save_flight_to_dict(primary),
            "simulated": [save_flight_to_dict(f) for f in simulated],
            "safety_buffer": safety_buffer,
            "is_3d": is_3d,
            "results": {
                "is_clear": is_clear,
                "num_conflicts": len(conflicts),
                "conflicts": [
                    {
                        "primary_flight": c.primary_flight_id,
                        "conflicting_flight": c.conflicting_flight_id,
                        "location": list(c.location),
                        "time": c.time,
                        "distance": c.min_distance
                    }
                    for c in conflicts
                ]
            }
        }
        
        with open(data_file, 'w') as f:
            json.dump(mission_data, f, indent=2)
        
        print(f"\\n✓ Mission data saved to {data_file}")
    
    print("\\n" + "="*70)
    print("Session Complete!")
    print("="*70)
    
    return is_clear, conflicts


def quick_scenario_mode():
    """
    Quick mode to select and run pre-built scenarios.
    """
    print("\\n" + "="*70)
    print("🚁 UAV DECONFLICTION SYSTEM - QUICK SCENARIO MODE")
    print("="*70)
    
    scenarios = get_all_scenarios()
    scenario_list = list(scenarios.keys())
    
    print("\\nAvailable scenarios:")
    for i, name in enumerate(scenario_list, 1):
        print(f"  {i}. {name}")
    
    while True:
        try:
            choice = int(input(f"\\nSelect scenario (1-{len(scenario_list)}): "))
            if 1 <= choice <= len(scenario_list):
                break
            print(f"❌ Please enter a number between 1 and {len(scenario_list)}.")
        except ValueError:
            print("❌ Invalid input! Please enter a number.")
    
    scenario_name = scenario_list[choice - 1]
    primary, simulated = scenarios[scenario_name]
    
    print(f"\\n✓ Selected: {scenario_name}")
    
    # Safety buffer
    while True:
        try:
            buffer_input = input("\\nSafety buffer (meters, default 10.0): ") or "10.0"
            safety_buffer = float(buffer_input)
            if safety_buffer > 0:
                break
            print("❌ Must be positive!")
        except ValueError:
            print("❌ Invalid input!")
    
    # Determine if 3D
    is_3d = primary.is_3d()
    
    # Visualization options
    show_anim = input("\\nShow animation? (y/n): ").lower() == 'y'
    save_viz = input("Save visualization? (y/n): ").lower() == 'y'
    
    output_file = None
    if save_viz:
        output_file = f"{scenario_name}_result.png"
    
    # Run check
    print("\\n" + "="*70)
    print("Running Analysis...")
    print("="*70)
    
    is_clear, conflicts = check_mission(
        primary, simulated,
        safety_buffer=safety_buffer,
        include_z=is_3d
    )
    
    # Results
    print("\\n" + generate_conflict_report(conflicts))
    
    # Visualization
    if is_3d:
        fig, ax = plot_3d_trajectories(primary, simulated, conflicts, safety_buffer)
    else:
        fig, ax = plot_2d_trajectories(primary, simulated, conflicts, safety_buffer)
    
    if output_file:
        save_visualization(fig, output_file)
    
    if show_anim and not is_3d:
        anim = animate_2d_trajectories(primary, simulated, conflicts, safety_buffer)
    
    plt.show()
    
    return is_clear, conflicts


def main():
    """Main entry point with mode selection."""
    parser = argparse.ArgumentParser(
        description='UAV Strategic Deconfliction System - Interactive Edition',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        choices=['interactive', 'quick', 'classic'],
        help='Interaction mode: interactive (full custom), quick (select scenario), classic (command-line)'
    )
    
    # Classic mode arguments (backward compatible)
    parser.add_argument('--scenario', type=str, help='Built-in scenario name')
    parser.add_argument('--input', type=str, help='JSON file with flight data')
    parser.add_argument('--buffer', type=float, default=10.0, help='Safety buffer (meters)')
    parser.add_argument('--3d', action='store_true', dest='use_3d', help='Enable 3D mode')
    parser.add_argument('--no-viz', action='store_true', help='Disable visualization')
    parser.add_argument('--animate', action='store_true', help='Generate animation')
    parser.add_argument('--output', type=str, help='Output file for visualization')
    
    args = parser.parse_args()
    
    # If no mode specified, ask user
    if not args.mode and not args.scenario and not args.input:
        print("\\n" + "="*70)
        print("🚁 UAV DECONFLICTION SYSTEM")
        print("="*70)
        print("\\nSelect mode:")
        print("  1. Interactive Mode (create custom missions step-by-step)")
        print("  2. Quick Scenario Mode (select from pre-built scenarios)")
        print("  3. Classic Mode (command-line with arguments)")
        
        while True:
            mode_input = input("\\nEnter choice (1-3): ").strip()
            if mode_input == '1':
                args.mode = 'interactive'
                break
            elif mode_input == '2':
                args.mode = 'quick'
                break
            elif mode_input == '3':
                args.mode = 'classic'
                break
            else:
                print("❌ Invalid choice! Please enter 1, 2, or 3.")
    
    # Route to appropriate mode
    if args.mode == 'interactive':
        is_clear, conflicts = interactive_mode()
    elif args.mode == 'quick':
        is_clear, conflicts = quick_scenario_mode()
    else:
        # Classic command-line mode (original functionality)
        from .cli import run_deconfliction_check, load_flights_from_json
        
        if args.scenario:
            scenarios = get_all_scenarios()
            if args.scenario not in scenarios:
                print(f"❌ Unknown scenario: {args.scenario}")
                sys.exit(1)
            primary, simulated = scenarios[args.scenario]
        elif args.input:
            primary, simulated = load_flights_from_json(args.input)
        else:
            print("❌ Must specify --scenario or --input in classic mode")
            parser.print_help()
            sys.exit(1)
        
        is_clear, conflicts = run_deconfliction_check(
            primary=primary,
            simulated=simulated,
            safety_buffer=args.buffer,
            include_z=args.use_3d,
            visualize=not args.no_viz,
            animate=args.animate,
            output_file=args.output
        )
    
    sys.exit(0 if is_clear else 1)


if __name__ == '__main__':
    main()
'''

with open("deconflict/src/interactive_cli.py", "w") as f:
    f.write(interactive_cli_content)

print("✓ Created interactive_cli.py with user input capabilities")
