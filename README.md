# State Utils

A collection of utilities for managing quam state configurations and related operations.

## Installation

```bash
pip install state-utils
```

## Usage

This package provides several utilities for managing quam state configurations:

### Frequency Collection and Analysis
The `collect_frequencies.py` script analyzes and displays frequency information from quam state configurations. It helps identify potential frequency conflicts and provides a clear overview of the frequency setup.

```bash
# Basic usage
python -m state_utils.collect_frequencies --state-path /path/to/state/directory
```

Example output:
```
Qubit Frequencies (sorted by total frequency):
------------------------------------------------------------------------------------------
Qubit     XY IF    XY LO XY Total    RR IF    RR LO RR Total
------------------------------------------------------------------------------------------
qC1     176.924    4.800    4.977 -226.732    7.380    7.153
qB1      59.844    4.950    5.010 -315.183    7.480    7.165
qA1     -34.250    5.050    5.016 -451.065    7.580    7.129
qC4     345.737    4.800    5.146 -109.808    7.380    7.270
qA4     231.102    4.950    5.181 -325.959    7.580    7.254
qD1     255.524    5.100    5.356 -306.558    7.460    7.153
qA2    -132.539    5.800    5.667 -182.538    7.580    7.397
qA3    -129.911    5.800    5.670  -88.478    7.580    7.492
qA5     -55.613    5.750    5.694   82.195    7.580    7.662
qB3      -4.120    5.700    5.696   52.520    7.480    7.533
qC3     115.673    5.590    5.706  143.591    7.380    7.524
qD5    -134.835    6.000    5.865  202.190    7.460    7.662
qB5     120.814    5.750    5.871  187.831    7.480    7.668
qC2     299.269    5.590    5.889   40.767    7.380    7.421
qD2     109.191    5.900    6.009  -51.607    7.460    7.408
qD3     161.182    5.900    6.061   63.685    7.460    7.524
qB2      78.189    6.000    6.078  -50.077    7.480    7.430
qC5     -28.442    6.250    6.222  281.051    7.380    7.661
qA6     149.920    6.250    6.400  178.849    7.580    7.759
qB4     292.668    6.300    6.593  262.801    7.480    7.743
qD4     293.407    6.300    6.593  278.263    7.460    7.738
```

This script:
- Extracts and displays XY and RR frequencies for each qubit
- Shows intermediate frequencies (IF) and local oscillator (LO) frequencies
- Sorts qubits by their total frequency
- Can save the output to a file for documentation

### Grid Location Management
The `collect_grid_locations.py` script extracts and manages the physical grid locations of qubits in the quantum processor.

```bash
# Basic usage
python -m state_utils.collect_grid_locations --state-path /path/to/state/directory
```

Example output:
```
grid_locations = {
    "qA1": "2,4",
    "qA2": "3,4",
    "qA3": "2,3",
    "qA4": "3,3",
    "qA5": "4,3",
    "qA6": "2,2",
    "qB1": "4,2",
    "qB2": "4,1",
    "qB3": "3,2",
    "qB4": "3,1",
    "qB5": "3,0",
    "qC1": "2,0",
    "qC2": "1,0",
    "qC3": "2,1",
    "qC4": "1,1",
    "qC5": "0,1",
    "qD1": "0,2",
    "qD2": "0,3",
    "qD3": "1,2",
    "qD4": "1,3",
    "qD5": "1,4",
}
```

This script:
- Extracts grid location information for all qubits
- Supports multiple output formats (JSON or Python dictionary)
- Useful for visualizing qubit layouts and planning connections
- Shows the 2D grid coordinates of each qubit in the processor

### Qubit Pair Analysis
The `collect_qubit_pairs.py` script analyzes and identifies qubit pairs, particularly focusing on nearest neighbors and frequency compatibility.

```bash
# Basic usage
python -m state_utils.collect_qubit_pairs --state-path /path/to/state/directory
```

Example output:
```
Printing Qubit Pairs (Control -> Target):
qA1-qA2: qA2 (5.667 GHz) -> qA1 (5.016 GHz)
qA1-qA3: qA3 (5.670 GHz) -> qA1 (5.016 GHz)
qA1-qD5: qD5 (5.865 GHz) -> qA1 (5.016 GHz)
qA2-qA4: qA2 (5.667 GHz) -> qA4 (5.181 GHz)
qA3-qA4: qA3 (5.670 GHz) -> qA4 (5.181 GHz)
qA3-qA6: qA6 (6.400 GHz) -> qA3 (5.670 GHz)
qA3-qD4: qD4 (6.593 GHz) -> qA3 (5.670 GHz)
qA4-qA5: qA5 (5.694 GHz) -> qA4 (5.181 GHz)
qA4-qB3: qB3 (5.696 GHz) -> qA4 (5.181 GHz)
qA5-qB1: qA5 (5.694 GHz) -> qB1 (5.010 GHz)
qA6-qB3: qA6 (6.400 GHz) -> qB3 (5.696 GHz)
qA6-qC3: qA6 (6.400 GHz) -> qC3 (5.706 GHz)
qA6-qD3: qA6 (6.400 GHz) -> qD3 (6.061 GHz)
qB1-qB2: qB2 (6.078 GHz) -> qB1 (5.010 GHz)
qB1-qB3: qB3 (5.696 GHz) -> qB1 (5.010 GHz)
qB2-qB4: qB4 (6.593 GHz) -> qB2 (6.078 GHz)
qB3-qB4: qB4 (6.593 GHz) -> qB3 (5.696 GHz)
qB4-qB5: qB4 (6.593 GHz) -> qB5 (5.871 GHz)
qB4-qC3: qB4 (6.593 GHz) -> qC3 (5.706 GHz)
qB5-qC1: qB5 (5.871 GHz) -> qC1 (4.977 GHz)
qC1-qC2: qC2 (5.889 GHz) -> qC1 (4.977 GHz)
qC1-qC3: qC3 (5.706 GHz) -> qC1 (4.977 GHz)
qC2-qC4: qC2 (5.889 GHz) -> qC4 (5.146 GHz)
qC3-qC4: qC3 (5.706 GHz) -> qC4 (5.146 GHz)
qC4-qC5: qC5 (6.222 GHz) -> qC4 (5.146 GHz)
qC4-qD3: qD3 (6.061 GHz) -> qC4 (5.146 GHz)
qC5-qD1: qC5 (6.222 GHz) -> qD1 (5.356 GHz)
qD1-qD2: qD2 (6.009 GHz) -> qD1 (5.356 GHz)
qD1-qD3: qD3 (6.061 GHz) -> qD1 (5.356 GHz)
qD2-qD4: qD4 (6.593 GHz) -> qD2 (6.009 GHz)
qD3-qD4: qD4 (6.593 GHz) -> qD3 (6.061 GHz)
qD4-qD5: qD4 (6.593 GHz) -> qD5 (5.865 GHz)
```

This script:
- Identifies nearest neighbor qubit pairs based on grid locations
- Analyzes frequency compatibility between pairs
- Can update the state file with pair information
- Color-codes frequencies based on their bands for easy visualization

### Other Utilities

#### State Configuration Workflow
The following scripts are designed to be run sequentially to create and configure a complete quam state setup:

1. **Generate Wiring Configuration**
```bash
python -m state_utils.make_wiring_lffem_mwfem --output wiring.json
```
This script:
- Creates the initial wiring configuration file
- Sets up the basic structure for low-frequency and microwave frequency connections
- Outputs a JSON file that defines the physical connections between components

2. **Create QUAM State**
```bash
python -m state_utils.make_quam --wiring-path wiring.json --output state.json
```
This script:
- Takes the wiring configuration as input
- Creates the initial state configuration
- Sets up basic parameters for all qubits and components
- Outputs a state JSON file that can be further modified

3. **Modify QUAM Configuration**
```bash
python -m state_utils.modify_quam --state-path state.json --output modified_state.json
```
This script:
- Takes the initial state configuration
- Applies custom modifications and optimizations
- Updates parameters based on specific requirements
- Outputs a final, modified state configuration

The typical workflow is:
1. Generate wiring configuration using `make_wiring_lffem_mwfem`
2. Create initial state using `make_quam` with the wiring configuration
3. Modify the state using `modify_quam` to achieve the desired configuration

Each script supports additional command-line arguments for fine-tuning the configuration. Use `--help` with any script to see available options.

- `state_to_cloud.py`: Upload quam state configurations to the cloud

## Development

To set up the development environment:

```bash
pip install -e ".[dev]"
```

## License

[Your chosen license]
