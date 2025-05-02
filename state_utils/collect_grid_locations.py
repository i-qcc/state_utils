#!/usr/bin/env python3
import json
import argparse
import os
from pathlib import Path

def collect_grid_locations(state_file_path):
    """Collect grid locations from a state file."""
    with open(state_file_path, 'r') as f:
        state = json.load(f)

    # Create dictionary to store grid locations
    grid_locations = {}

    # Collect grid locations for all qubits
    for qubit_name, qubit_data in state['qubits'].items():
        if 'grid_location' in qubit_data:
            grid_locations[qubit_name] = qubit_data['grid_location']

    return grid_locations

def main():
    parser = argparse.ArgumentParser(description='Collect grid locations from a state file')
    parser.add_argument('--state-path', type=str, default=os.environ.get('QUAM_STATE_PATH'),
                      help='Path to the directory containing state.json (default: QUAM_STATE_PATH environment variable)')
    parser.add_argument('--output', type=str, help='Path to save the grid locations as JSON (optional)')
    parser.add_argument('--format', choices=['python', 'json'], default='python',
                      help='Output format (default: python)')
    args = parser.parse_args()

    if not args.state_path:
        raise ValueError("State path not provided and QUAM_STATE_PATH environment variable not set")

    # Convert path to Path object
    state_dir = Path(args.state_path)
    state_path = state_dir / "state.json"

    if not state_path.exists():
        raise FileNotFoundError(f"State file not found: {state_path}")

    # Collect grid locations
    grid_locations = collect_grid_locations(state_path)

    # Save to file if requested
    if args.output:
        output_path = Path(args.output)
        if args.format == 'json':
            with open(output_path, 'w') as f:
                json.dump(grid_locations, f, indent=2)
        else:
            with open(output_path, 'w') as f:
                f.write("grid_locations = {\n")
                for qubit, location in sorted(grid_locations.items()):
                    f.write(f'    "{qubit}": "{location}",\n')
                f.write("}\n")
        print(f"Grid locations saved to {output_path}")

    # Print to console
    if args.format == 'json':
        print(json.dumps(grid_locations, indent=2))
    else:
        print("grid_locations = {")
        for qubit, location in sorted(grid_locations.items()):
            print(f'    "{qubit}": "{location}",')
        print("}")

if __name__ == '__main__':
    main() 