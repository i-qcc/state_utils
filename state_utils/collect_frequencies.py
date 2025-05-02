#!/usr/bin/env python3
import json
import numpy as np
import argparse
import os
from pathlib import Path

# ANSI escape codes for text formatting
RED = '\033[91m'
RESET = '\033[0m'

def format_frequency(freq, threshold=400):
    """Format frequency with red if it's close to threshold in absolute value"""
    freq_str = f"{freq:8.3f}"  # Fixed width of 8 characters
    if abs(freq) > threshold:
        return f"{RED}{freq_str}{RESET}"
    return freq_str

def extract_frequencies(state_file_path, wiring_file_path):
    # Load both files
    with open(state_file_path, 'r') as f:
        state = json.load(f)
    with open(wiring_file_path, 'r') as f:
        wiring = json.load(f)
    
    # Initialize lists to store frequencies
    qubit_names = []
    xy_if_freqs = []
    xy_lo_freqs = []
    xy_total_freqs = []
    rr_if_freqs = []
    rr_lo_freqs = []
    rr_total_freqs = []
    
    # Create a mapping of port IDs to their frequencies
    port_freq_map = {}
    for controller_id, controller_data in state['ports']['mw_outputs'].items():
        for fem_id, fem_data in controller_data.items():
            for port_id, port_data in fem_data.items():
                # Only add ports that have upconverter_frequency
                if 'upconverter_frequency' in port_data:
                    port_freq_map[(controller_id, int(fem_id), int(port_id))] = port_data['upconverter_frequency']
    
    # Extract frequencies for each qubit
    for qubit_name, qubit_data in state['qubits'].items():
        # XY frequencies
        if 'xy' in qubit_data:
            # Get intermediate frequency
            xy_if_freq = qubit_data['xy'].get('intermediate_frequency', 0)
            
            # Get port information from wiring
            if qubit_name in wiring['wiring']['qubits']:
                # XY port reference
                xy_port_ref = wiring['wiring']['qubits'][qubit_name]['xy']['opx_output']
                if xy_port_ref.startswith('#/ports/mw_outputs/'):
                    # Extract port information from the reference
                    path_parts = xy_port_ref.split('/')
                    controller_id = path_parts[3]
                    fem_id = int(path_parts[4])
                    port_id = int(path_parts[5])
                    
                    # Get LO frequency from our mapping
                    xy_lo_freq = port_freq_map.get((controller_id, fem_id, port_id))
                    if xy_lo_freq is not None:
                        # Calculate total frequency
                        xy_total_freq = xy_lo_freq + xy_if_freq
                        
                        # RR frequencies
                        if 'resonator' in qubit_data:
                            rr_if_freq = qubit_data['resonator'].get('intermediate_frequency', 0)
                            
                            # Get RR port reference
                            rr_port_ref = wiring['wiring']['qubits'][qubit_name]['rr']['opx_output']
                            if rr_port_ref.startswith('#/ports/mw_outputs/'):
                                # Extract port information from the reference
                                path_parts = rr_port_ref.split('/')
                                controller_id = path_parts[3]
                                fem_id = int(path_parts[4])
                                port_id = int(path_parts[5])
                                
                                # Get LO frequency from our mapping
                                rr_lo_freq = port_freq_map.get((controller_id, fem_id, port_id))
                                if rr_lo_freq is not None:
                                    # Calculate total frequency
                                    rr_total_freq = rr_lo_freq + rr_if_freq
                                    
                                    # Store all values
                                    qubit_names.append(qubit_name)
                                    xy_if_freqs.append(xy_if_freq)
                                    xy_lo_freqs.append(xy_lo_freq)
                                    xy_total_freqs.append(xy_total_freq)
                                    rr_if_freqs.append(rr_if_freq)
                                    rr_lo_freqs.append(rr_lo_freq)
                                    rr_total_freqs.append(rr_total_freq)
    
    # Create a structured output
    output = {
        'qubit': qubit_names,
        'xy_intermediate_frequency': xy_if_freqs,
        'xy_lo_frequency': xy_lo_freqs,
        'xy_total_frequency': xy_total_freqs,
        'rr_intermediate_frequency': rr_if_freqs,
        'rr_lo_frequency': rr_lo_freqs,
        'rr_total_frequency': rr_total_freqs
    }
    
    return output

def main():
    parser = argparse.ArgumentParser(description='Collect and display frequency information from a state file')
    parser.add_argument('--state-path', type=str, default=os.environ.get('QUAM_STATE_PATH'),
                      help='Path to the directory containing state.json (default: QUAM_STATE_PATH environment variable)')
    parser.add_argument('--wiring-path', type=str, help='Path to the wiring file (default: wiring.json in state directory)')
    parser.add_argument('--output', type=str, help='Path to save the output (optional)')
    parser.add_argument('--threshold', type=float, default=400, help='Threshold for highlighting frequencies (default: 400 MHz)')
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

    # Extract frequencies
    frequencies = extract_frequencies(state_path, wiring_path)
    
    # Save to file if requested
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w') as f:
            json.dump(frequencies, f, indent=2)
        print(f"Frequencies saved to {output_path}")
    
    # Create a list of tuples for sorting
    qubit_data = list(zip(
        frequencies['qubit'],
        frequencies['xy_intermediate_frequency'],
        frequencies['xy_lo_frequency'],
        frequencies['xy_total_frequency'],
        frequencies['rr_intermediate_frequency'],
        frequencies['rr_lo_frequency'],
        frequencies['rr_total_frequency']
    ))
    
    # Sort by total frequency
    qubit_data.sort(key=lambda x: x[3])  # x[3] is xy_total_freq
    
    # Print results in a table format
    print("\nQubit Frequencies (sorted by total frequency):")
    print("-" * 90)
    print(f"{'Qubit':<6} {'XY IF':>8} {'XY LO':>8} {'XY Total':>8} {'RR IF':>8} {'RR LO':>8} {'RR Total':>8}")
    print("-" * 90)
    
    for qubit, xy_if, xy_lo, xy_total, rr_if, rr_lo, rr_total in qubit_data:
        # Convert to appropriate units
        xy_if_freq = xy_if / 1e6
        xy_lo_freq = xy_lo / 1e9
        xy_total_freq = xy_total / 1e9
        rr_if_freq = rr_if / 1e6
        rr_lo_freq = rr_lo / 1e9
        rr_total_freq = rr_total / 1e9
        
        # Format frequencies with red if they're close to threshold
        xy_if_freq_str = format_frequency(xy_if_freq, args.threshold)
        rr_if_freq_str = format_frequency(rr_if_freq, args.threshold)
        
        # Print with fixed column widths
        print(f"{qubit:<6} {xy_if_freq_str:>8} {xy_lo_freq:8.3f} {xy_total_freq:8.3f} {rr_if_freq_str:>8} {rr_lo_freq:8.3f} {rr_total_freq:8.3f}")

if __name__ == '__main__':
    main() 