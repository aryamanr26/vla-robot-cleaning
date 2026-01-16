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

    # Task-level preference (high-level reasoning)
    if task == "clean":
        dst = node_by_id.get(edge["to"], {})
        priority = dst.get("priority")
        if priority in PRIORITY_TO_PENALTY:
            cost += PRIORITY_TO_PENALTY[priority]

    # Contextual penalty (crowds, time of day, etc.)
    if context.get("crowded", False) and edge.get("skill") == "enter_zone":
        cost += 0.3

    # -------------------------------
    # EXECUTION-LEVEL RISK MODELING
    # -------------------------------

    # Reliability penalty (only if specified in JSON)
    reliability = edge.get("reliability", 1.0)
    cost += (1.0 - reliability) * 3.0

    # Temporary block from failed execution
    blocked = context.get("blocked_edges", [])
    edge_id = (edge["from"], edge["to"])
    if edge_id in blocked:
        cost += 100.0  # effectively disables this edge

    return max(0.01, cost)