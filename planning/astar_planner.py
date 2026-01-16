from typing import Any, Dict, List, Optional, Tuple
import networkx as nx

from planning.planner_interface import Planner, PlanResult
from planning.costs import compute_edge_cost


class NetworkXAStarPlanner(Planner):
    def _build_nx_graph(self, graph: Dict[str, Any], context: Optional[Dict[str, Any]]) -> nx.DiGraph:
        G = nx.DiGraph()

        nodes = graph["nodes"]
        edges = graph["edges"]

        node_by_id = {n["id"]: n for n in nodes}

        for n in nodes:
            G.add_node(n["id"], **n)

        for e in edges:
            cost = compute_edge_cost(e, node_by_id=node_by_id, context=context)
            # store full edge payload for downstream execution
            edge_payload = dict(e)
            edge_payload["cost"] = cost
            G.add_edge(e["from"], e["to"], **edge_payload, weight=cost)

        return G

    def plan(
        self,
        graph: Dict[str, Any],
        start: str,
        goal: str,
        context: Optional[Dict[str, Any]] = None
    ) -> PlanResult:
        G = self._build_nx_graph(graph, context=context)

        node_path: List[str] = nx.astar_path(G, start, goal, weight="weight")

        edge_path: List[Dict[str, Any]] = []
        for u, v in zip(node_path[:-1], node_path[1:]):
            edge_path.append(dict(G.edges[u, v]))

        return PlanResult(nodes=node_path, edges=edge_path)
