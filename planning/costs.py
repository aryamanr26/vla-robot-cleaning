from typing import Any, Dict, Optional


PRIORITY_TO_PENALTY = {
    "high": -0.2,   # prefer reaching high priority zones
    "medium": 0.0,
    "low": 0.2
}


def compute_edge_cost(
    edge: Dict[str, Any],
    node_by_id: Dict[str, Dict[str, Any]],
    context: Optional[Dict[str, Any]] = None
) -> float:
    context = context or {}
    task = context.get("task", "navigate")

    cost = float(edge.get("base_cost", 1.0))

    # Example: if task is "clean", make it slightly cheaper to go toward high priority zones
    if task == "clean":
        dst = node_by_id.get(edge["to"], {})
        priority = dst.get("priority")
        if priority in PRIORITY_TO_PENALTY:
            cost += PRIORITY_TO_PENALTY[priority]

    # Example: add penalties for risky skills in crowded mode
    if context.get("crowded", False) and edge.get("skill") == "enter_zone":
        cost += 0.3

    return max(0.01, cost)
