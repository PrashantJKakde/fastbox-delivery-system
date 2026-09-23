"""
Test Runner for FastBox Delivery System
Validates the delivery_system.py against all provided test cases.
"""

import json
import os
import sys
import math
import copy

# Import our delivery system module
sys.path.insert(0, os.path.dirname(__file__))
from delivery_system import (
    euclidean_distance,
    assign_packages_to_agents,
    simulate_deliveries,
    find_best_agent,
    generate_report,
    run_simulation,
)


def run_test(test_file: str) -> dict:
    """Run the simulation against a single test case JSON file."""
    with open(test_file, "r") as f:
        data = json.load(f)

    warehouses = data["warehouses"]
    agents = data["agents"]
    packages = data["packages"]

    # Assign packages
    assignments = assign_packages_to_agents(warehouses, agents, packages)

    # Simulate deliveries
    results = simulate_deliveries(agents, warehouses, assignments)

    # Find best agent
    best_agent = find_best_agent(results)

    # Generate report
    report = generate_report(results, best_agent)

    return report


def validate_report(report: dict, packages: list, agents: dict) -> list:
    """Validate the report for correctness."""
    errors = []

    # Check all agents are present
    for agent_id in agents:
        if agent_id not in report:
            errors.append(f"Missing agent {agent_id} in report")

    # Check total packages delivered matches input
    total_delivered = sum(
        report[aid]["packages_delivered"]
        for aid in agents
        if aid in report
    )
    if total_delivered != len(packages):
        errors.append(
            f"Total packages delivered ({total_delivered}) != "
            f"total packages ({len(packages)})"
        )

    # Check best_agent is in report
    if "best_agent" not in report:
        errors.append("Missing 'best_agent' in report")
    elif report["best_agent"] not in agents:
        errors.append(f"best_agent '{report['best_agent']}' is not a valid agent")

    # Check efficiency consistency
    for agent_id in agents:
        if agent_id in report:
            data = report[agent_id]
            pkgs = data["packages_delivered"]
            dist = data["total_distance"]
            eff = data["efficiency"]
            if pkgs > 0:
                expected_eff = round(dist / pkgs, 2)
                if abs(expected_eff - eff) > 0.01:
                    errors.append(
                        f"{agent_id} efficiency mismatch: "
                        f"got {eff}, expected {expected_eff}"
                    )

    return errors


def main():
    test_dir = "Python Assignment(Delivery System Test Cases)"
    test_files = sorted(
        [f for f in os.listdir(test_dir) if f.endswith(".json")],
        key=lambda x: int(x.split("_")[-1].replace(".json", ""))
    )

    print("=" * 60)
    print("FastBox Delivery System - Test Runner")
    print("=" * 60)

    all_passed = True

    for test_file in test_files:
        filepath = os.path.join(test_dir, test_file)
        print(f"\nRunning: {test_file}")

        # Load original data
        with open(filepath, "r") as f:
            data = json.load(f)

        # Run simulation
        try:
            report = run_test(filepath)

            # Validate
            errors = validate_report(
                report, data["packages"], data["agents"]
            )

            if errors:
                print(f"  FAIL - Errors:")
                for err in errors:
                    print(f"    - {err}")
                all_passed = False
            else:
                total_pkgs = len(data["packages"])
                total_delivered = sum(
                    report[aid]["packages_delivered"]
                    for aid in data["agents"]
                )
                best = report["best_agent"]
                print(f"  PASS - {total_delivered}/{total_pkgs} packages delivered, best_agent={best}")
                # Show each agent summary
                for agent_id in sorted(data["agents"].keys()):
                    d = report[agent_id]
                    print(f"    {agent_id}: {d['packages_delivered']} pkgs, dist={d['total_distance']}, eff={d['efficiency']}")

        except Exception as e:
            print(f"  ERROR - {e}")
            import traceback
            traceback.print_exc()
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
