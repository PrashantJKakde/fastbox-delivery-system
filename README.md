# FastBox Delivery System

A Python simulation of a logistics delivery system for the fictional company **FastBox**.

## Overview

This project simulates one day of delivery operations:

1. **Parses** input data from `data.json` containing warehouses, delivery agents, and packages
2. **Assigns** each package to the nearest available agent (based on Euclidean distance from agent to warehouse)
3. **Simulates** each delivery: agent travels from current position ? warehouse ? destination
4. **Computes** total distance traveled per agent and efficiency (distance per package)
5. **Identifies** the best agent (lowest efficiency score)
6. **Outputs** a `report.json` with the results

## Project Structure

```
.
+-- delivery_system.py          # Main simulation script
+-- test_runner.py              # Test runner for all test cases
+-- data.json                   # Default input data file (generated from base_case)
+-- base_case.json              # Base input case (list format)
+-- report.json                 # Output report (generated on run)
+-- Python Assignment(Delivery System Test Cases)/
    +-- test_case_1.json        # Test inputs
    +-- test_case_2.json
    +-- ...                     # (10 total test cases)
```

## Input Format

The `data.json` file should have:

```json
{
    "warehouses": {
        "W1": [x, y],
        "W2": [x, y]
    },
    "agents": {
        "A1": [x, y],
        "A2": [x, y]
    },
    "packages": [
        {"id": "P1", "warehouse": "W1", "destination": [x, y]}
    ]
}
```

## Output Format

The `report.json` file contains:

```json
{
    "A1": {"packages_delivered": 2, "total_distance": 85.32, "efficiency": 42.66},
    "A2": {"packages_delivered": 2, "total_distance": 120.12, "efficiency": 60.06},
    "best_agent": "A1"
}
```

- `packages_delivered`: Number of packages this agent delivered
- `total_distance`: Total Euclidean distance traveled (rounded to 2 decimal places)
- `efficiency`: Average distance per package (`total_distance / packages_delivered`)
- `best_agent`: Agent with the lowest efficiency value (most efficient)

## Usage

### Run with default data.json

```bash
python delivery_system.py
```

### Run with a custom input file

```bash
python delivery_system.py path/to/input.json path/to/output.json
```

### Run all test cases

```bash
python test_runner.py
```

## Algorithm

### Package Assignment

For each package:
- Calculate Euclidean distance from every agent to the package's warehouse
- Assign the package to the agent with the shortest distance
- Distance formula: `sqrt((x2-x1)^2 + (y2-y1)^2)`

### Delivery Simulation

For each agent, process packages in assigned order:
- `distance += euclidean(current_pos, warehouse)`
- `distance += euclidean(warehouse, destination)`
- Agent position updates to the destination after each delivery

### Best Agent Selection

The best agent is the one with the lowest **efficiency** value (i.e., the smallest average distance per package delivered). Only agents who delivered at least one package are considered.

## Requirements

- Python 3.6+
- No external dependencies (uses only standard library: `json`, `math`, `sys`, `os`)

## Test Results

All 10 provided test cases pass validation:
- Total packages delivered always equals total input packages
- All agents appear in the report
- Efficiency values are consistent with distances
