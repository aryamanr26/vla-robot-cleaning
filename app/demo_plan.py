import json
from planning.astar_planner import NetworkXAStarPlanner


def main():
    with open("world_model/topological_graph.json", "r") as f:
        graph = json.load(f)

    planner = NetworkXAStarPlanner()

    context = {"task": "clean", "crowded": True}
    result = planner.plan(graph, start="dock", goal="championship_court", context=context)

    print("Node path:")
    print(" -> ".join(result.nodes))

    print("\nEdge skills:")
    for e in result.edges:
        print(f'{e["from"]} -> {e["to"]} | skill={e["skill"]} | cost={e["cost"]:.2f}')


if __name__ == "__main__":
    main()
