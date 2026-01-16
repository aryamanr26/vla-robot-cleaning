import json
import random
import networkx as nx
from planning.astar_planner import NetworkXAStarPlanner
from task.cleaning_task_planner import plan_cleaning_tasks


def simulate_edge_execution(edge):
    reliability = edge.get("reliability", 1.0)
    return random.random() < reliability


def main():
    with open("world_model/topological_graph.json") as f:
        graph = json.load(f)

    task_list = plan_cleaning_tasks(graph, policy="priority_first")

    print("\nPlanned cleaning order:")
    for z in task_list:
        print(f" - {z}")

    planner = NetworkXAStarPlanner()

    context = {
        "task": "clean",
        "blocked_edges": []
    }

    current = "dock"

    # -----------------------------
    # STEP 3: EXECUTE TASKS SEQUENTIALLY
    # -----------------------------
    for goal in task_list:
        print(f"\n=== Navigating to clean: {goal} ===")

        while current != goal:
            try:
                plan = planner.plan(graph, current, goal, context)
            except nx.NetworkXNoPath:
                print(f"No path from {current} to {goal}, skipping zone.")
                break

            # plan = planner.plan(graph, current, goal, context)

            next_edge = plan.edges[0]
            print(f"Attempting: {next_edge['from']} → {next_edge['to']}")

            success = simulate_edge_execution(next_edge)

            if success:
                print("✓ Success")
                current = next_edge["to"]
            else:
                print("✗ FAILED, replanning")
                context["blocked_edges"].append(
                    (next_edge["from"], next_edge["to"])
                )

        print(f"✓ Finished cleaning zone: {goal}")

    print("\nAll assigned zones cleaned. Returning to dock.")

    # Optional: return to dock
    if current != "dock":
        while current != "dock":
            plan = planner.plan(graph, current, "dock", context)
            next_edge = plan.edges[0]
            current = next_edge["to"]

    print("✓ Docked successfully.")



if __name__ == "__main__":
    main()
