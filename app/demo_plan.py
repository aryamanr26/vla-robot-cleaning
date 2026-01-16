import json
import random
import networkx as nx

from planning.astar_planner import NetworkXAStarPlanner
from task.cleaning_task_planner import plan_cleaning_tasks

# --- VLM imports (INTENTIONALLY NOT USED AT RUNTIME) ---
# These are placeholders for future VLM/VLA integration
from vlm.vlm_task_grounder import VLMTaskGrounder
from task.cleaning_task_planner import plan_cleaning_tasks_from_vlm


def simulate_edge_execution(edge):
    """Simulate probabilistic execution success."""
    reliability = edge.get("reliability", 1.0)
    return random.random() < reliability


def main():
    # -----------------------------
    # LOAD WORLD MODEL
    # -----------------------------
    with open("world_model/topological_graph.json") as f:
        graph = json.load(f)

    # -----------------------------
    # TASK PLANNING (STATIC POLICY)
    # -----------------------------
    # NOTE:
    # In a full VLA system, this task list would be generated
    # by a Vision-Language Model (VLM) based on human instructions.
    #
    # For this challenge, we intentionally use a deterministic,
    # policy-based planner to keep the system executable without
    # external model dependencies.
    #
    # Example (disabled):
    # vlm = VLMTaskGrounder()
    # vlm_output = vlm.ground_task("Clean the entrance area")
    # task_list = plan_cleaning_tasks_from_vlm(vlm_output, graph)

    task_list = plan_cleaning_tasks(graph, policy="priority_first")

    print("\nPlanned cleaning order:")
    for z in task_list:
        print(f" - {z}")

    # -----------------------------
    # NAVIGATION PLANNER
    # -----------------------------
    planner = NetworkXAStarPlanner()

    context = {
        "task": "clean",
        "blocked_edges": []
    }

    current = "dock"

    # -----------------------------
    # EXECUTE TASKS SEQUENTIALLY
    # -----------------------------
    for goal in task_list:
        print(f"\n=== Navigating to clean: {goal} ===")

        while current != goal:
            try:
                plan = planner.plan(graph, current, goal, context)
            except nx.NetworkXNoPath:
                print(f"No path from {current} to {goal}, skipping zone.")
                break

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

    # -----------------------------
    # RETURN TO DOCK
    # -----------------------------
    print("\nAll assigned zones cleaned. Returning to dock.")

    if current != "dock":
        while current != "dock":
            try:
                plan = planner.plan(graph, current, "dock", context)
            except nx.NetworkXNoPath:
                print("No path back to dock. Manual intervention required.")
                return

            next_edge = plan.edges[0]
            current = next_edge["to"]

    print("✓ Docked successfully.")


if __name__ == "__main__":
    main()
