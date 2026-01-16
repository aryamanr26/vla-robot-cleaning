import json
import random
import networkx as nx

from planning.astar_planner import NetworkXAStarPlanner
from task.cleaning_task_planner import plan_cleaning_tasks

# --- VLM imports (INTENTIONALLY NOT USED AT RUNTIME) ---
# Placeholders for future VLM/VLA integration
from vlm.vlm_task_grounder import VLMTaskGrounder
from task.cleaning_task_planner import plan_cleaning_tasks_from_vlm

# --- OEM Abstraction (MOCK ONLY) ---
from oem.mock_robot import MockRobot

# --- Console UI helpers ---
from ui.console import banner, section, log, ok, fail


def simulate_edge_execution(edge):
    """Simulate probabilistic execution success."""
    reliability = edge.get("reliability", 1.0)
    return random.random() < reliability


def main():
    banner("Autonomous Cleaning Mission")

    # -----------------------------
    # LOAD WORLD MODEL
    # -----------------------------
    with open("world_model/topological_graph.json") as f:
        graph = json.load(f)
    log("World model loaded")

    # -----------------------------
    # INITIALIZE ROBOT (OEM-AGNOSTIC)
    # -----------------------------
    robot = MockRobot()
    robot.connect()
    log("Robot connected (mock)")

    # -----------------------------
    # TASK PLANNING (STATIC POLICY)
    # -----------------------------
    # NOTE:
    # VLM-based task grounding is intentionally disabled
    # for this challenge to ensure executability.
    #
    # Example (disabled):
    # vlm = VLMTaskGrounder()
    # vlm_output = vlm.ground_task("Clean the entrance area")
    # task_list = plan_cleaning_tasks_from_vlm(vlm_output, graph)

    task_list = plan_cleaning_tasks(graph, policy="priority_first")

    section("Planned Cleaning Order")
    for i, z in enumerate(task_list, 1):
        log(f"{i}. {z}")

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
        section(f"Navigating to clean: {goal}")

        while current != goal:
            try:
                plan = planner.plan(graph, current, goal, context)
            except nx.NetworkXNoPath:
                fail(f"No path from {current} to {goal}, skipping zone")
                break

            next_edge = plan.edges[0]
            log(f"Navigate {next_edge['from']} -> {next_edge['to']}")

            success = simulate_edge_execution(next_edge)

            if success:
                ok(f"Reached {next_edge['to']}")
                robot.navigate_to_node(next_edge["to"])
                current = next_edge["to"]
            else:
                fail("Traversal failed, replanning")
                context["blocked_edges"].append(
                    (next_edge["from"], next_edge["to"])
                )

        # -----------------------------
        # CLEANING EXECUTION (ABSTRACTED)
        # -----------------------------
        log("Start cleaning (zone_clean)")
        robot.start_cleaning(mode="zone_clean")
        robot.stop_cleaning()
        ok(f"Zone cleaned: {goal}")

    # -----------------------------
    # RETURN TO DOCK
    # -----------------------------
    section("Return to Dock")

    if current != "dock":
        while current != "dock":
            try:
                plan = planner.plan(graph, current, "dock", context)
            except nx.NetworkXNoPath:
                fail("No path back to dock. Manual intervention required.")
                return

            next_edge = plan.edges[0]
            log(f"Navigate {next_edge['from']} -> {next_edge['to']}")
            robot.navigate_to_node(next_edge["to"])
            current = next_edge["to"]

    ok("Docked successfully")
    banner("Mission Complete")


if __name__ == "__main__":
    main()
