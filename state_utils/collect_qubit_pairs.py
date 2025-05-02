#!/usr/bin/env python3
import json
import argparse
import os
from pathlib import Path
from collections import defaultdict
from .collect_frequencies import extract_frequencies

# ANSI color codes
RED = '\033[91m'
GREEN = '\033[92m'
BLUE = '\033[94m'
RESET = '\033[0m'

def get_frequency_color(freq_ghz):
    """Return the appropriate color code based on frequency band"""
    if freq_ghz >= 6.375:
        return RED
    elif freq_ghz >= 5.6:
        return BLUE
    else:
        return GREEN

def parse_grid_location(location_str):
    """Parse grid location string into x,y coordinates"""
    x, y = map(int, location_str.split(','))
    return (x, y)

def find_nearest_neighbors(state):
    """Find all nearest neighbor pairs of qubits"""
    # Create dictionary to store grid locations
    grid_locations = {}
    for qubit_name, qubit_data in state['qubits'].items():
        if 'grid_location' in qubit_data:
            grid_locations[qubit_name] = parse_grid_location(qubit_data['grid_location'])
    
    # Find nearest neighbors
    nearest_neighbors = []
    qubit_names = list(grid_locations.keys())
    
    for i in range(len(qubit_names)):
        for j in range(i + 1, len(qubit_names)):
            q1 = qubit_names[i]
            q2 = qubit_names[j]
            x1, y1 = grid_locations[q1]
            x2, y2 = grid_locations[q2]
            
            # Check if qubits are adjacent (differ by 1 in either x or y)
            if (abs(x1 - x2) == 1 and y1 == y2) or (abs(y1 - y2) == 1 and x1 == x2):
                nearest_neighbors.append((q1, q2))
    
    return nearest_neighbors

def collect_qubit_pairs(state_file_path, wiring_file_path, write_to_state=False):
    """Collect and optionally write qubit pairs to state file."""
    # Load the state file
    with open(state_file_path, 'r') as f:
        state = json.load(f)
    
    # Get qubit frequencies using the existing function
    frequencies_data = extract_frequencies(state_file_path, wiring_file_path)
    
    # Create a dictionary of total frequencies
    frequencies = {}
    for qubit, xy_total in zip(frequencies_data['qubit'], frequencies_data['xy_total_frequency']):
        frequencies[qubit] = xy_total
    
    # Find nearest neighbors
    nearest_neighbors = find_nearest_neighbors(state)
    
    # Create qubit_pairs dictionary
    qubit_pairs = {}
    
    if write_to_state:
        print("\nCreating Qubit Pairs in State File (Control -> Target):")
    else:
        print("\nPrinting Qubit Pairs (Control -> Target):")
    
    for q1, q2 in nearest_neighbors:
        # Determine control and target based on frequency
        if frequencies[q1] > frequencies[q2]:
            control, target = q1, q2
        else:
            control, target = q2, q1
        
        # Create pair key and data
        pair_key = f"{q1}-{q2}"
        qubit_pairs[pair_key] = {
            "id": pair_key,
            "qubit_control": f"#/qubits/{control}",
            "qubit_target": f"#/qubits/{target}"
        }
        
        freq_control_ghz = frequencies[control]/1e9
        freq_target_ghz = frequencies[target]/1e9
        color_control = get_frequency_color(freq_control_ghz)
        color_target = get_frequency_color(freq_target_ghz)
        print(f"{pair_key}: {control} ({color_control}{freq_control_ghz:.3f}{RESET} GHz) -> {target} ({color_target}{freq_target_ghz:.3f}{RESET} GHz)")
    
    if write_to_state:
        # Add qubit_pairs to state
        state['qubit_pairs'] = qubit_pairs
        
        # Save updated state
        with open(state_file_path, 'w') as f:
            json.dump(state, f, indent=4)
        
        print(f"\nSuccessfully created {len(qubit_pairs)} qubit pairs in state file")
    else:
        print(f"\nFound {len(qubit_pairs)} qubit pairs (not written to state file)")
    
    return qubit_pairs

def main():
    parser = argparse.ArgumentParser(description='Collect and analyze qubit pairs from state and wiring files')
    parser.add_argument('--state-path', type=str, default=os.environ.get('QUAM_STATE_PATH'),
                      help='Path to the directory containing state.json (default: QUAM_STATE_PATH environment variable)')
    parser.add_argument('--wiring-path', type=str, help='Path to the wiring file (default: wiring.json in state directory)')
    parser.add_argument('--write-to-state', action='store_true',
                      help='Write the qubit pairs back to the state file')
    parser.add_argument('--output', type=str, help='Path to save qubit pairs as JSON (optional)')
    args = parser.parse_args()

    if not args.state_path:
        raise ValueError("State path not provided and QUAM_STATE_PATH environment variable not set")

    # Convert paths to Path objects
    state_dir = Path(args.state_path)
    state_path = state_dir / "state.json"
    
    # If wiring path not provided, use wiring.json in the same directory
    if args.wiring_path:
        wiring_path = Path(args.wiring_path)
    else:
        wiring_path = state_dir / "wiring.json"

    if not state_path.exists():
        raise FileNotFoundError(f"State file not found: {state_path}")
    if not wiring_path.exists():
        raise FileNotFoundError(f"Wiring file not found: {wiring_path}")

    # Collect qubit pairs
    qubit_pairs = collect_qubit_pairs(state_path, wiring_path, args.write_to_state)

    # Save to separate file if requested
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w') as f:
            json.dump(qubit_pairs, f, indent=4)
        print(f"\nQubit pairs saved to {output_path}")

if __name__ == "__main__":
    main() 