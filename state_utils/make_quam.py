#!/usr/bin/env python3
import argparse
from pathlib import Path
from quam_libs.components import QuAM
from quam_libs.quam_builder.machine import build_quam

def create_quam(
    state_path: Path,
    octave_ip: str = None,
    octave_port: int = None,
    overwrite: bool = False
):
    """Create a QuAM configuration from a state directory."""
    # Check if state directory exists
    if not state_path.exists():
        raise FileNotFoundError(f"State directory not found: {state_path}")

    # Load machine
    machine = QuAM.load(state_path)

    # Configure octave settings
    octave_settings = {}
    if octave_ip:
        octave_settings = {"octave1": {"ip": octave_ip}}
    elif octave_port:
        octave_settings = {"octave1": {"port": octave_port}}

    # Make the QuAM object and save it
    quam = build_quam(machine, quam_state_path=str(state_path), octaves_settings=octave_settings)
    return quam

def main():
    parser = argparse.ArgumentParser(description='Create a QuAM configuration from a state directory')
    parser.add_argument('--state-path', type=str, required=True, help='Path to the state directory')
    parser.add_argument('--octave-ip', type=str, help='IP address of the Octave (optional)')
    parser.add_argument('--octave-port', type=int, help='Port of the Octave (optional)')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing files')
    args = parser.parse_args()

    # Convert path to Path object
    state_path = Path(args.state_path)

    try:
        quam = create_quam(
            state_path=state_path,
            octave_ip=args.octave_ip,
            octave_port=args.octave_port,
            overwrite=args.overwrite
        )
        print(f"QuAM configuration created successfully in {state_path}")
    except Exception as e:
        print(f"Error creating QuAM configuration: {e}")
        raise

if __name__ == '__main__':
    main() 