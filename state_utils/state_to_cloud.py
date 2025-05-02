#!/usr/bin/env python3
import json
import os
import argparse
from pathlib import Path
from quam_libs.lib.iqcc_cloud_storage_utils import save_quam_state_to_cloud
from iqcc_cloud_client import IQCC_Cloud

def main():
    parser = argparse.ArgumentParser(description='Upload quantum state to cloud storage')
    parser.add_argument('--state-path', type=str, help='Path to the state directory (default: QUAM_STATE_PATH env var)')
    parser.add_argument('--wiring-file', type=str, default='wiring.json', help='Name of the wiring file (default: wiring.json)')
    parser.add_argument('--state-file', type=str, default='state.json', help='Name of the state file (default: state.json)')
    args = parser.parse_args()

    # Determine state path
    quam_state_folder_path = args.state_path or os.environ.get("QUAM_STATE_PATH")
    if not quam_state_folder_path:
        raise ValueError("State path must be provided either via --state-path or QUAM_STATE_PATH environment variable")

    # Convert to Path object for better path handling
    quam_state_folder_path = Path(quam_state_folder_path)
    wiring_path = quam_state_folder_path / args.wiring_file
    state_path = quam_state_folder_path / args.state_file

    # Upload state to cloud
    save_quam_state_to_cloud()

    # Load local wiring and state
    with open(wiring_path, "r") as f:
        local_wiring = json.load(f)
    
    with open(state_path, "r") as f:
        local_state = json.load(f)

    # Initialize cloud client
    quantum_computer_backend = local_wiring["network"]["quantum_computer_backend"]
    qc = IQCC_Cloud(quantum_computer_backend=quantum_computer_backend)

    # Get latest cloud state
    latest_wiring = qc.state.get_latest("wiring")
    latest_state = qc.state.get_latest("state")

    # Verify data matches
    assert latest_state.data == local_state, "The latest state dataset does not match the state.json data"
    assert latest_wiring.data == local_wiring, "The latest wiring dataset does not match the wiring.json data"

    print("Successfully uploaded and verified state data")

if __name__ == "__main__":
    main() 