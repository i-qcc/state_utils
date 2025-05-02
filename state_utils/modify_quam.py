#!/usr/bin/env python3
import json
import os
import argparse
import numpy as np
from pathlib import Path
from qualang_tools.units import unit
from quam_libs.components import QuAM
from quam_libs.components.transmon import Transmon
from quam_libs.quam_builder.machine import save_machine

def get_band(freq):
    """Determine the band for a given frequency."""
    if 50e6 <= freq < 4.5e9:
        return 1
    elif 4.5e9 <= freq < 6.5e9:
        return 2
    elif 6.5e9 <= freq <= 10.5e9:
        return 3
    else:
        raise ValueError(f"The specified frequency {freq} HZ is outside of the MW fem bandwidth [50 MHz, 10.5 GHz]")

def modify_quam(qubits: Transmon, *, rr_LO, xy_LO, rr_if, xy_if, rr_max_power_dBm, xy_max_power_dBm):
    """Modify QUAM configuration for a set of qubits."""
    for i, q in enumerate(qubits):
        # Update qubit rr freq and power
        machine.qubits[q].resonator.opx_output.full_scale_power_dbm = rr_max_power_dBm
        machine.qubits[q].resonator.opx_output.upconverter_frequency = rr_LO[i]
        machine.qubits[q].resonator.opx_input.downconverter_frequency = rr_LO[i]
        machine.qubits[q].resonator.opx_input.band = get_band(rr_LO[i])
        machine.qubits[q].resonator.opx_output.band = get_band(rr_LO[i])
        machine.qubits[q].resonator.intermediate_frequency = rr_if[i]

        # Update qubit xy freq and power
        machine.qubits[q].xy.opx_output.full_scale_power_dbm = xy_max_power_dBm
        machine.qubits[q].xy.opx_output.upconverter_frequency = xy_LO[i]
        machine.qubits[q].xy.opx_output.band = get_band(xy_LO[i])
        machine.qubits[q].xy.intermediate_frequency = xy_if[i]

        # Update flux channels
        machine.qubits[q].z.opx_output.output_mode = "direct"
        machine.qubits[q].z.opx_output.upsampling_mode = "pulse"

        # Update pulses
        # readout
        machine.qubits[q].resonator.operations["readout"].length = 1.5 * u.us
        machine.qubits[q].resonator.operations["readout"].amplitude = 1e-2
        # Qubit saturation
        machine.qubits[q].xy.operations["saturation"].length = 20 * u.us
        machine.qubits[q].xy.operations["saturation"].amplitude = 0.25
        # Single qubit gates - DragCosine
        machine.qubits[q].xy.operations["x180_DragCosine"].length = 48
        machine.qubits[q].xy.operations["x180_DragCosine"].amplitude = 0.2
        machine.qubits[q].xy.operations["x90_DragCosine"].amplitude = (
            machine.qubits[q].xy.operations["x180_DragCosine"].amplitude / 2
        )
        # Single qubit gates - Square
        machine.qubits[q].xy.operations["x180_Square"].length = 40
        machine.qubits[q].xy.operations["x180_Square"].amplitude = 0.1
        machine.qubits[q].xy.operations["x90_Square"].amplitude = (
            machine.qubits[q].xy.operations["x180_Square"].amplitude / 2
        )

def load_config(config_path):
    """Load configuration from a JSON file."""
    with open(config_path, 'r') as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser(description='Modify QUAM configuration')
    parser.add_argument('--state-path', type=str, required=True, help='Path to the state directory')
    parser.add_argument('--config-path', type=str, help='Path to the configuration JSON file')
    parser.add_argument('--output-path', type=str, help='Path to save the modified state (default: same as input)')
    parser.add_argument('--qua-config-path', type=str, help='Path to save the QUA configuration (default: qua_config.json)')
    args = parser.parse_args()

    # Convert paths to Path objects
    state_path = Path(args.state_path)
    if not state_path.exists():
        raise FileNotFoundError(f"State directory not found: {state_path}")

    # Load machine
    global machine
    machine = QuAM.load(state_path)
    global u
    u = unit(coerce_to_integer=True)

    # Load configuration if provided
    if args.config_path:
        config = load_config(args.config_path)
        # Apply configuration here
        # This is a placeholder - you'll need to implement the actual configuration application
        pass

    # Group qubits by their letter
    qubitsA = [q for q in machine.qubits.keys() if q[1] == "A"]
    qubitsB = [q for q in machine.qubits.keys() if q[1] == "B"]
    qubitsC = [q for q in machine.qubits.keys() if q[1] == "C"]
    qubitsD = [q for q in machine.qubits.keys() if q[1] == "D"]

    # Set active qubits
    machine.active_qubit_names = qubitsA + qubitsB + qubitsC + qubitsD

    # Define grid locations
    grid = {
        "qA1": "2,4", "qA2": "3,4", "qA3": "2,3", "qA4": "3,3", "qA5": "4,3", "qA6": "2,2",
        "qB1": "4,2", "qB2": "4,1", "qB3": "3,2", "qB4": "3,1", "qB5": "3,0",
        "qC1": "2,0", "qC2": "1,0", "qC3": "2,1", "qC4": "1,1", "qC5": "0,1",
        "qD1": "0,2", "qD2": "0,3", "qD3": "1,2", "qD4": "1,3", "qD5": "1,4"
    }

    # Apply grid locations
    for name, qubit in machine.qubits.items():
        qubit.grid_location = grid[name]

    # Add threading settings
    for name, qubit in machine.qubits.items():
        qubit.xy.thread = name
        qubit.resonator.thread = name

    # Add explicit decouple_offset
    for name, qubit_pair in machine.qubit_pairs.items():
        qubit_pair.coupler.decouple_offset = 0.0

    # Save modified state
    output_path = args.output_path or state_path
    save_machine(machine, output_path)

    # Save QUA configuration
    qua_config_path = args.qua_config_path or "qua_config.json"
    with open(qua_config_path, "w+") as f:
        json.dump(machine.generate_config(), f, indent=4)

    print(f"Modified state saved to {output_path}")
    print(f"QUA configuration saved to {qua_config_path}")

if __name__ == '__main__':
    main() 