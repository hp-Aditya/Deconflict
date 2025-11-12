"""
Interactive command-line interface with user input capabilities.
"""
import argparse
import json
import sys
from typing import List
from .data_models import Flight, Waypoint, save_flight_to_dict
from .detector_enhanced import check_mission_high_accuracy, generate_conflict_report
from .viz import plot_2d_trajectories, plot_3d_trajectories, animate_2d_trajectories, animate_3d_trajectories, save_visualization
from .example_scenarios import get_all_scenarios
import matplotlib.pyplot as plt


def get_waypoints_interactive(drone_id: str, is_3d: bool = False) -> List[Waypoint]:
    """Get waypoints from user input."""
    print(f"\n{'='*60}")
    print(f"Enter waypoints for {drone_id}")
    print(f"{'='*60}")
    print("Tip: You need at least 2 waypoints. Press Ctrl+C to cancel.\n")

    waypoints = []
    waypoint_num = 1

    while True:
        print(f"Waypoint #{waypoint_num}:")

        try:
            x = float(input(f"  X (meters): "))
            y = float(input(f"  Y (meters): "))
            z = float(input(f"  Z/Altitude (meters, 0 for 2D): ")) if is_3d else 0.0

            waypoints.append(Waypoint(x, y, z))

            if waypoint_num >= 2:
                more = input(f"  Add another waypoint? (y/n): ").lower()
                if more != 'y':
                    break

            waypoint_num += 1

        except ValueError:
            print("  ❌ Invalid! Enter numbers only.")
            continue
        except KeyboardInterrupt:
            print("\n  Cancelled.")
            sys.exit(0)

    return waypoints


def create_flight_interactive(flight_id: str, is_3d: bool = False) -> Flight:
    """Create a Flight from user input."""
    print(f"\n{'='*60}")
    print(f"Configure: {flight_id}")
    print(f"{'='*60}")

    waypoints = get_waypoints_interactive(flight_id, is_3d)

    print(f"\nTiming:")
    while True:
        try:
            t_start = float(input(f"  Start time (sec, default 0): ") or "0")
            t_end = float(input(f"  End time (sec): "))

            if t_end <= t_start:
                print("  ❌ End time must be > start time!")
                continue
            break
        except ValueError:
            print("  ❌ Invalid number!")

    while True:
        try:
            speed = float(input(f"  Speed (m/s, default 5.0): ") or "5.0")
            if speed > 0:
                break
            print("  ❌ Speed must be positive!")
        except ValueError:
            print("  ❌ Invalid number!")

    return Flight(id=flight_id, waypoints=waypoints, 
                 t_start=t_start, t_end=t_end, speed=speed)


def interactive_session():
    """Full interactive session."""
    print("\n" + "="*70)
    print("🚁 UAV DECONFLICTION - INTERACTIVE MODE")
    print("="*70)

    # Mode selection
    print("\n1. 2D Mode (X, Y)")
    print("2. 3D Mode (X, Y, Z)")
    while True:
        mode = input("\nChoice (1/2): ").strip()
        if mode in ['1', '2']:
            is_3d = (mode == '2')
            break
        print("❌ Enter 1 or 2")

    print(f"\n✓ {'3D' if is_3d else '2D'} mode selected\n")

    # Create primary
    print("="*70)
    print("CREATE PRIMARY DRONE")
    print("="*70)
    primary = create_flight_interactive("PRIMARY", is_3d)
    print(f"✓ Primary: {len(primary.waypoints)} waypoints")

    # Create simulated
    print("\n" + "="*70)
    print("CREATE SIMULATED DRONES")
    print("="*70)

    while True:
        try:
            num = int(input("\nNumber of simulated drones (1-10): "))
            if 1 <= num <= 10:
                break
            print("❌ Enter 1-10")
        except ValueError:
            print("❌ Invalid number!")

    simulated = []
    for i in range(num):
        print(f"\n--- Simulated Drone {i+1}/{num} ---")
        simulated.append(create_flight_interactive(f"SIM_{i+1:02d}", is_3d))

    # Safety buffer
    print("\n" + "="*70)
    print("SAFETY CONFIGURATION")
    print("="*70)

    while True:
        try:
            buffer = float(input("\nSafety buffer (m, default 10.0): ") or "10.0")
            if buffer > 0:
                break
            print("❌ Must be positive!")
        except ValueError:
            print("❌ Invalid!")

    # Accuracy level - FIXED: removed leading space from '1' key
    print("\nSimulation accuracy:")
    print("  1. Standard (20 samples) - Fast")
    print("  2. High (50 samples) - Balanced")
    print("  3. Ultra (100 samples) - Most accurate")

    while True:
        acc = input("\nChoice (1-3, default 2): ").strip() or "2"
        if acc in ['1', '2', '3']:
            samples = {'1': 20, '2': 50, '3': 100}[acc]  # FIXED: removed space before '1'
            break
        print("❌ Enter 1, 2, or 3")

    # Visualization
    print("\n" + "="*70)
    print("VISUALIZATION")
    print("="*70)

    print("\n1. Static plot only")
    print("2. Static + Animation")
    print("3. No visualization")

    while True:
        viz = input("\nChoice (1-3): ").strip()
        if viz in ['1', '2', '3']:
            break
        print("❌ Enter 1, 2, or 3")

    show_viz = viz != '3'
    animate = viz == '2'

    save_file = None
    if show_viz:
        if input("\nSave plot? (y/n): ").lower() == 'y':
            save_file = input("Filename (default: result.png): ").strip() or "result.png"
            if not save_file.endswith('.png'):
                save_file += '.png'

    # Run analysis
    print("\n" + "="*70)
    print("RUNNING ANALYSIS...")
    print("="*70)

    print(f"\n📊 Config: {len(simulated)} drones, {buffer:.1f}m buffer, {samples} samples")

    is_clear, conflicts = check_mission_high_accuracy(
        primary, simulated, buffer, is_3d, samples
    )

    # Results
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"\n{generate_conflict_report(conflicts)}")

    if not is_clear:
        print(f"⚠️  {len(conflicts)} conflicts - Mission UNSAFE")
    else:
        print("✅ Mission SAFE")

    # Visualize
    if show_viz:
        print("\nGenerating visualization...")

        if is_3d:
            fig, ax = plot_3d_trajectories(primary, simulated, conflicts, buffer)
        else:
            fig, ax = plot_2d_trajectories(primary, simulated, conflicts, buffer)

        if save_file:
            save_visualization(fig, save_file)

        # ADDED: 3D animation support
        if animate:
            print("Creating animation...")
            if is_3d:
                anim = animate_3d_trajectories(primary, simulated, conflicts, buffer)
            else:
                anim = animate_2d_trajectories(primary, simulated, conflicts, buffer)

            if save_file:
                anim_file = save_file.replace('.png', '.gif')
                try:
                    anim.save(anim_file, writer='pillow', fps=20)
                    print(f"✓ Saved to {anim_file}")
                except Exception as e:
                    print(f"⚠️  Animation save failed: {e}")

        plt.show()

    # Save data
    if input("\nSave mission JSON? (y/n): ").lower() == 'y':
        data_file = input("Filename (default: mission.json): ").strip() or "mission.json"
        if not data_file.endswith('.json'):
            data_file += '.json'

        data = {
            "primary": save_flight_to_dict(primary),
            "simulated": [save_flight_to_dict(f) for f in simulated],
            "config": {"buffer": buffer, "is_3d": is_3d, "samples": samples},
            "results": {
                "safe": is_clear,
                "conflicts": len(conflicts)
            }
        }

        with open(data_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✓ Saved to {data_file}")

    print("\n" + "="*70)
    print("Complete!")
    print("="*70)

    return is_clear


def quick_scenario():
    """Quick scenario selection."""
    print("\n" + "="*70)
    print("🚁 QUICK SCENARIO MODE")
    print("="*70)

    scenarios = get_all_scenarios()
    names = list(scenarios.keys())

    print("\nScenarios:")
    for i, name in enumerate(names, 1):
        print(f"  {i}. {name}")

    while True:
        try:
            choice = int(input(f"\nSelect (1-{len(names)}): "))
            if 1 <= choice <= len(names):
                break
        except ValueError:
            pass
        print(f"❌ Enter 1-{len(names)}")

    name = names[choice - 1]
    primary, simulated = scenarios[name]

    print(f"\n✓ {name}")

    buffer = float(input("Buffer (m, default 10): ") or "10")
    is_3d = primary.is_3d()

    # Accuracy - FIXED: removed leading space
    print("\nAccuracy: 1=Fast, 2=Balanced, 3=Ultra")
    acc = input("Choice (default 2): ").strip() or "2"
    samples = {'1': 20, '2': 50, '3': 100}.get(acc, 50)

    animate = input("Animate? (y/n): ").lower() == 'y'

    print("\nAnalyzing...")
    is_clear, conflicts = check_mission_high_accuracy(
        primary, simulated, buffer, is_3d, samples
    )

    print(f"\n{generate_conflict_report(conflicts)}")

    # Create visualization
    if is_3d:
        fig, _ = plot_3d_trajectories(primary, simulated, conflicts, buffer)
        if animate:
            print("Creating 3D animation...")
            anim = animate_3d_trajectories(primary, simulated, conflicts, buffer)
    else:
        fig, _ = plot_2d_trajectories(primary, simulated, conflicts, buffer)
        if animate:
            print("Creating 2D animation...")
            anim = animate_2d_trajectories(primary, simulated, conflicts, buffer)

    plt.show()
    return is_clear


def main():
    """Main entry."""
    parser = argparse.ArgumentParser(description='UAV Deconfliction - Interactive')
    parser.add_argument('--mode', choices=['interactive', 'quick'], 
                       help='Mode: interactive or quick')

    args = parser.parse_args()

    if not args.mode:
        print("\n" + "="*70)
        print("🚁 UAV DECONFLICTION SYSTEM")
        print("="*70)
        print("\n1. Interactive (custom missions)")
        print("2. Quick (select scenario)")

        while True:
            choice = input("\nChoice (1/2): ").strip()
            if choice == '1':
                args.mode = 'interactive'
                break
            elif choice == '2':
                args.mode = 'quick'
                break
            print("❌ Enter 1 or 2")

    if args.mode == 'interactive':
        is_clear = interactive_session()
    else:
        is_clear = quick_scenario()

    sys.exit(0 if is_clear else 1)


if __name__ == '__main__':
    main()