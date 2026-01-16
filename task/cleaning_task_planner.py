from typing import Dict, Any, List

def plan_cleaning_tasks_from_vlm(vlm_output, graph):
    """
    Convert VLM output into an ordered task list.
    """

    target_zones = vlm_output.get("target_zones", [])

    # Filter to zones that actually exist
    zone_ids = {n["id"] for n in graph["nodes"]}
    valid_targets = [z for z in target_zones if z in zone_ids]

    # Simple ordering for now (can be extended)
    return valid_targets

def plan_cleaning_tasks(
    graph: Dict[str, Any],
    policy: str = "priority_first"
) -> List[str]:
    """
    Decide which cleaning zones to visit and in what order.
    This is task-level reasoning, independent of navigation.
    """

    # Extract cleaning zones
    zones = [
        node for node in graph["nodes"]
        if node.get("type") == "cleaning_zone"
    ]

    if policy == "priority_first":
        priority_rank = {
            "high": 0,
            "medium": 1,
            "low": 2
        }

        zones.sort(
            key=lambda z: priority_rank.get(
                z.get("priority", "medium"), 1
            )
        )

    elif policy == "high_only":
        zones = [
            z for z in zones
            if z.get("priority") == "high"
        ]

    # Return ordered list of zone IDs
    return [z["id"] for z in zones]
