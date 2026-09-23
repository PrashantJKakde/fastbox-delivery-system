"""
FastBox Delivery System Simulator
==================================
Simulates one day of operations for the FastBox delivery company.

Steps:
1. Read and parse data.json (supports both list-of-objects and dict formats)
2. Assign each package to the nearest agent (by Euclidean distance: agent to warehouse)
3. Simulate delivery: agent travels agent_pos -> warehouse -> destination
4. Compute total distance traveled per agent
5. Compute efficiency = total_distance / packages_delivered
6. Identify the best agent (lowest efficiency = least distance per package)
7. Save report to report.json
"""

import json
import math
import sys
import os


def euclidean_distance(point1, point2):
    """Calculate the Euclidean distance between two 2D points [x1,y1] and [x2,y2]."""
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def normalize_data(data):
    """
    Normalize input data to a canonical format regardless of input schema.

    Supports two warehouse/agent formats:
      - Dict format (test cases): {"W1": [x, y], "W2": [x, y], ...}
      - List format (base_case):  [{"id": "W1", "location": [x, y]}, ...]

    Packages always follow the list format but may use "warehouse_id" or "warehouse"
    as the warehouse reference key.

    Returns:
        (warehouses_dict, agents_dict, packages_list)
        where warehouses_dict = {id: [x, y]}
              agents_dict     = {id: [x, y]}
              packages_list   = [{"id": ..., "warehouse": ..., "destination": [...]}, ...]
    """
    # Normalize warehouses
    raw_warehouses = data["warehouses"]
    if isinstance(raw_warehouses, dict):
        # Already in dict format: {"W1": [x, y], ...}
        warehouses = raw_warehouses
    elif isinstance(raw_warehouses, list):
        # List of objects: [{"id": "W1", "location": [x, y]}, ...]
        warehouses = {}
        for w in raw_warehouses:
            loc = w.get("location", w.get("loc", None))
            warehouses[w["id"]] = loc
    else:
        raise ValueError(f"Unsupported warehouses format: {type(raw_warehouses)}")

    # Normalize agents
    raw_agents = data["agents"]
    if isinstance(raw_agents, dict):
        # Already in dict format: {"A1": [x, y], ...}
        agents = raw_agents
    elif isinstance(raw_agents, list):
        # List of objects: [{"id": "A1", "location": [x, y]}, ...]
        agents = {}
        for a in raw_agents:
            loc = a.get("location", a.get("loc", None))
            agents[a["id"]] = loc
    else:
        raise ValueError(f"Unsupported agents format: {type(raw_agents)}")

    # Normalize packages - ensure we use "warehouse" key consistently
    raw_packages = data["packages"]
    packages = []
    for pkg in raw_packages:
        normalized_pkg = {
            "id": pkg["id"],
            # Support both "warehouse" and "warehouse_id" keys
            "warehouse": pkg.get("warehouse", pkg.get("warehouse_id")),
            "destination": pkg["destination"],
        }
        packages.append(normalized_pkg)

    return warehouses, agents, packages


def load_data(filepath):
    """Load, parse and normalize the JSON input data file."""
    with open(filepath, "r") as f:
        data = json.load(f)
    return normalize_data(data)


def assign_packages_to_agents(warehouses, agents, packages):
    """
    Assign each package to the nearest agent based on Euclidean distance
    from the agent current position to the package warehouse location.

    Returns:
        Dict mapping agent_id -> list of packages assigned to that agent.
    """
    # Initialize assignment dictionary with all agents (even unassigned ones)
    assignments = {agent_id: [] for agent_id in agents}

    for package in packages:
        warehouse_id = package["warehouse"]
        warehouse_loc = warehouses[warehouse_id]

        # Find nearest agent to this package's warehouse
        nearest_agent = None
        min_distance = float("inf")

        for agent_id, agent_loc in agents.items():
            dist = euclidean_distance(agent_loc, warehouse_loc)
            if dist < min_distance:
                min_distance = dist
                nearest_agent = agent_id

        # Assign the package to the nearest agent
        assignments[nearest_agent].append(package)

    return assignments


def simulate_deliveries(agents, warehouses, assignments):
    """
    Simulate delivery operations for all agents.

    For each package assigned to an agent:
      - Agent travels: current_pos -> warehouse -> destination
      - Agent position updates to destination after each delivery

    Returns:
        Dict: agent_id -> {packages_delivered, total_distance, efficiency}
    """
    results = {}

    for agent_id, agent_start in agents.items():
        packages = assignments.get(agent_id, [])

        total_distance = 0.0
        # Agent starts at their initial position
        current_pos = list(agent_start)

        for package in packages:
            warehouse_loc = warehouses[package["warehouse"]]
            destination = package["destination"]

            # Travel segment 1: current position -> warehouse
            dist_to_warehouse = euclidean_distance(current_pos, warehouse_loc)

            # Travel segment 2: warehouse -> destination
            dist_to_destination = euclidean_distance(warehouse_loc, destination)

            total_distance += dist_to_warehouse + dist_to_destination

            # Agent is now at the destination after delivery
            current_pos = list(destination)

        packages_delivered = len(packages)
        total_distance = round(total_distance, 2)

        # Efficiency = average distance per package delivered
        if packages_delivered > 0:
            efficiency = round(total_distance / packages_delivered, 2)
        else:
            efficiency = 0.0

        results[agent_id] = {
            "packages_delivered": packages_delivered,
            "total_distance": total_distance,
            "efficiency": efficiency,
        }

    return results


def find_best_agent(results):
    """
    Find the most efficient agent (lowest efficiency = least distance per package).
    Only considers agents who delivered at least one package.
    """
    # Only consider agents who delivered at least one package
    active_agents = {
        agent_id: data
        for agent_id, data in results.items()
        if data["packages_delivered"] > 0
    }

    if not active_agents:
        # No deliveries; return the first agent alphabetically
        return sorted(results.keys())[0]

    # Best agent = lowest efficiency value
    best_agent = min(active_agents, key=lambda aid: active_agents[aid]["efficiency"])
    return best_agent


def generate_report(results, best_agent):
    """Generate the final report dictionary."""
    report = {}
    for agent_id, data in results.items():
        report[agent_id] = {
            "packages_delivered": data["packages_delivered"],
            "total_distance": data["total_distance"],
            "efficiency": data["efficiency"],
        }
    report["best_agent"] = best_agent
    return report


def save_report(report, filepath):
    """Save the report dictionary to a JSON file."""
    with open(filepath, "w") as f:
        json.dump(report, f, indent=4)
    print(f"Report saved to: {filepath}")


def run_simulation(input_file="data.json", output_file="report.json"):
    """Run the full FastBox delivery simulation."""
    # Step 1: Load and normalize data
    print(f"Loading data from: {input_file}")
    warehouses, agents, packages = load_data(input_file)

    print(f"  Warehouses: {list(warehouses.keys())}")
    print(f"  Agents:     {list(agents.keys())}")
    print(f"  Packages:   {len(packages)}")

    # Step 2: Assign packages to nearest agents
    print("\nAssigning packages to nearest agents...")
    assignments = assign_packages_to_agents(warehouses, agents, packages)

    for agent_id, pkgs in assignments.items():
        pkg_ids = [p["id"] for p in pkgs]
        print(f"  {agent_id}: {pkg_ids}")

    # Step 3: Simulate deliveries
    print("\nSimulating deliveries...")
    results = simulate_deliveries(agents, warehouses, assignments)

    # Step 4: Find the best agent
    best_agent = find_best_agent(results)

    # Step 5: Generate report
    report = generate_report(results, best_agent)

    # Print summary
    print("\n--- Delivery Report ---")
    for agent_id in sorted(results.keys()):
        data = results[agent_id]
        print(
            f"  {agent_id}: {data['packages_delivered']} pkgs, "
            f"dist={data['total_distance']}, "
            f"efficiency={data['efficiency']}"
        )
    print(f"  Best agent: {best_agent}")

    # Step 6: Save report to file
    save_report(report, output_file)

    return report


if __name__ == "__main__":
    # Allow optional command-line override of input/output files
    input_file = sys.argv[1] if len(sys.argv) > 1 else "data.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "report.json"

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)

    run_simulation(input_file, output_file)
