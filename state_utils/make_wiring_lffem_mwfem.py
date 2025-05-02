#!/usr/bin/env python3
import json
import os
import argparse
from pathlib import Path
from qualang_tools.wirer.wirer.channel_specs import *
from qualang_tools.wirer import Instruments, Connectivity, allocate_wiring, visualize
from quam_libs.quam_builder.machine import build_quam_wiring

def create_wiring(
    output_path: Path,
    host_ip: str = "10.1.1.11",
    port: int = None,
    cluster_name: str = "Cluster_1",
    quantum_computer_backend: str = "qc_qwtune",
    overwrite: bool = False
):
    """Create wiring configuration for LFFEM and MWFEM setup."""
    # Delete existing state.json and wiring.json files if they exist and overwrite is True
    state_file = output_path / "state.json"
    wiring_file = output_path / "wiring.json"
    
    if overwrite:
        if state_file.exists():
            state_file.unlink()
        if wiring_file.exists():
            wiring_file.unlink()
    elif state_file.exists() or wiring_file.exists():
        raise FileExistsError("State or wiring files already exist. Use --overwrite to replace them.")

    # Define the available instrument setup
    instruments = Instruments()
    instruments.add_mw_fem(controller=1, slots=[1,2,3,4])
    instruments.add_lf_fem(controller=1, slots=[5,6,7,8])

    # Define which qubit indices are present in the system
    qubitsA = ["A1", "A2", "A3", "A4", "A5", "A6"]
    qubitsB = ["B1", "B2", "B3", "B4", "B5"]
    qubitsC = ["C1", "C2", "C3", "C4", "C5"]
    qubitsD = ["D1", "D2", "D3", "D4", "D5"]
    qubits = qubitsA + qubitsB + qubitsC + qubitsD

    # Must be list of tuples, each tuple is a pair of qubits that are coupled
    qubit_pairs = []  # no couplers

    # Allocate the wiring to the connectivity object based on the available instruments
    connectivity = Connectivity()

    # Define any custom/hardcoded channel addresses
    q_drive_chs = [
        mw_fem_spec(con=1, slot=4, out_port=2),  # A1
        mw_fem_spec(con=1, slot=4, out_port=3),  # A2
        mw_fem_spec(con=1, slot=4, out_port=4),  # A3
        mw_fem_spec(con=1, slot=4, out_port=5),  # A4
        mw_fem_spec(con=1, slot=4, out_port=6),  # A5
        mw_fem_spec(con=1, slot=4, out_port=7),  # A6
        mw_fem_spec(con=1, slot=1, out_port=2),  # B1
        mw_fem_spec(con=1, slot=1, out_port=3),  # B2
        mw_fem_spec(con=1, slot=1, out_port=4),  # B3
        mw_fem_spec(con=1, slot=1, out_port=5),  # B4
        mw_fem_spec(con=1, slot=1, out_port=6),  # B5
        mw_fem_spec(con=1, slot=2, out_port=2),  # C1
        mw_fem_spec(con=1, slot=2, out_port=3),  # C2
        mw_fem_spec(con=1, slot=2, out_port=4),  # C3
        mw_fem_spec(con=1, slot=2, out_port=5),  # C4
        mw_fem_spec(con=1, slot=2, out_port=6),  # C5
        mw_fem_spec(con=1, slot=3, out_port=2),  # D1
        mw_fem_spec(con=1, slot=3, out_port=3),  # D2
        mw_fem_spec(con=1, slot=3, out_port=4),  # D3
        mw_fem_spec(con=1, slot=3, out_port=5),  # D4
        mw_fem_spec(con=1, slot=3, out_port=6),  # D5
    ]

    q_flux_chs = [
        lf_fem_spec(con=1, out_slot=8, out_port=1),  # A1
        lf_fem_spec(con=1, out_slot=8, out_port=2),  # A2
        lf_fem_spec(con=1, out_slot=8, out_port=3),  # A3
        lf_fem_spec(con=1, out_slot=8, out_port=4),  # A4
        lf_fem_spec(con=1, out_slot=8, out_port=5),  # A5
        lf_fem_spec(con=1, out_slot=8, out_port=6),  # A6
        lf_fem_spec(con=1, out_slot=5, out_port=1),  # B1
        lf_fem_spec(con=1, out_slot=5, out_port=2),  # B2
        lf_fem_spec(con=1, out_slot=5, out_port=3),  # B3
        lf_fem_spec(con=1, out_slot=5, out_port=4),  # B4
        lf_fem_spec(con=1, out_slot=5, out_port=5),  # B5
        lf_fem_spec(con=1, out_slot=7, out_port=1),  # C1
        lf_fem_spec(con=1, out_slot=7, out_port=2),  # C2
        lf_fem_spec(con=1, out_slot=7, out_port=3),  # C3
        lf_fem_spec(con=1, out_slot=7, out_port=4),  # C4
        lf_fem_spec(con=1, out_slot=7, out_port=5),  # C5
        lf_fem_spec(con=1, out_slot=6, out_port=1),  # D1
        lf_fem_spec(con=1, out_slot=6, out_port=2),  # D2
        lf_fem_spec(con=1, out_slot=6, out_port=3),  # D3
        lf_fem_spec(con=1, out_slot=6, out_port=4),  # D4
        lf_fem_spec(con=1, out_slot=6, out_port=5),  # D5
    ]

    # Single feed-line for reading the resonators & individual qubit drive lines
    qA_res_ch = mw_fem_spec(con=1, slot=4, in_port=1, out_port=1)
    qB_res_ch = mw_fem_spec(con=1, slot=1, in_port=1, out_port=1)
    qC_res_ch = mw_fem_spec(con=1, slot=2, in_port=1, out_port=1)
    qD_res_ch = mw_fem_spec(con=1, slot=3, in_port=1, out_port=1)

    connectivity.add_resonator_line(qubits=qubitsA, constraints=qA_res_ch)
    connectivity.add_resonator_line(qubits=qubitsB, constraints=qB_res_ch)
    connectivity.add_resonator_line(qubits=qubitsC, constraints=qC_res_ch)
    connectivity.add_resonator_line(qubits=qubitsD, constraints=qD_res_ch)

    for i in range(len(qubits)):
        connectivity.add_qubit_flux_lines(qubits=qubits[i], constraints=q_flux_chs[i])
        connectivity.add_qubit_drive_lines(qubits=qubits[i], constraints=q_drive_chs[i])

    allocate_wiring(connectivity, instruments)

    # Build the wiring and network into a QuAM machine and save it as "wiring.json"
    build_quam_wiring(connectivity, host_ip, cluster_name, str(output_path), port)

    # Add quantum_computer_backend and cloud to the wiring.network
    wiring_path = output_path / "wiring.json"
    with open(wiring_path, "r") as f:
        wiring = json.load(f)
    wiring["network"]["quantum_computer_backend"] = quantum_computer_backend
    wiring["network"]["cloud"] = True
    with open(wiring_path, "w") as f:
        json.dump(wiring, f, indent=4)

    # View wiring schematic
    visualize(connectivity.elements, available_channels=instruments.available_channels)

def main():
    parser = argparse.ArgumentParser(description='Create wiring configuration for LFFEM and MWFEM setup')
    parser.add_argument('--output-path', type=str, required=True, help='Path to save the wiring configuration')
    parser.add_argument('--host-ip', type=str, default="10.1.1.11", help='QOP IP address')
    parser.add_argument('--port', type=int, help='QOP Port')
    parser.add_argument('--cluster-name', type=str, default="Cluster_1", help='Name of the cluster')
    parser.add_argument('--quantum-computer-backend', type=str, default="qc_qwtune", help='Quantum computer backend name')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing files')
    args = parser.parse_args()

    # Convert path to Path object
    output_path = Path(args.output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    try:
        create_wiring(
            output_path=output_path,
            host_ip=args.host_ip,
            port=args.port,
            cluster_name=args.cluster_name,
            quantum_computer_backend=args.quantum_computer_backend,
            overwrite=args.overwrite
        )
        print(f"Wiring configuration created successfully in {output_path}")
    except Exception as e:
        print(f"Error creating wiring configuration: {e}")
        raise

if __name__ == '__main__':
    main() 