from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class PlanResult:
    nodes: List[str]
    edges: List[Dict[str, Any]]  # each edge dict includes from, to, skill, cost


class Planner:
    def plan(
        self,
        graph: Dict[str, Any],
        start: str,
        goal: str,
        context: Optional[Dict[str, Any]] = None
    ) -> PlanResult:
        raise NotImplementedError
