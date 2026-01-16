import json
import random
from planning.astar_planner import NetworkXAStarPlanner


def simulate_edge_execution(edge):
    reliability = edge.get("reliability", 1.0)
    return random.random() < reliability


def main():
    with open("world_model/topological_graph.json") as f:
        graph = json.load(f)

    planner = NetworkXAStarPlanner()

    context = {
        "task": "clean",
        "blocked_edges": []
    }

    current = "dock"
    goal = "championship_court"

    while current != goal:
        plan = planner.plan(graph, current, goal, context)

        next_edge = plan.edges[0]
        print(f"\nAttempting: {next_edge['from']} → {next_edge['to']}")

        success = simulate_edge_execution(next_edge)

        if success:
            print("✓ Success")
            current = next_edge["to"]
        else:
            print("✗ FAILED, replanning")
            context["blocked_edges"].append(
                (next_edge["from"], next_edge["to"])
            )

    print("\nReached goal!")


if __name__ == "__main__":
    main()
