# Kineti-Tec Challenge 01 - Part B Implementation
# 1. Simplified Perception/Mapping Pipeline
# 2. Navigation Planner over Topological Graph

import numpy as np
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import heapq
from pathlib import Path

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Pose2D:
    """Robot pose in 2D space"""
    x: float
    y: float
    theta: float  # orientation in radians
    
    def distance_to(self, other: 'Pose2D') -> float:
        """Euclidean distance to another pose"""
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

@dataclass
class GraphNode:
    """Node in topological graph"""
    id: int
    pose: Pose2D
    semantic_label: Optional[str] = None
    zone_id: Optional[str] = None
    image_embedding: Optional[List[float]] = None  # CLIP embedding (simulated)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'pose': asdict(self.pose),
            'semantic_label': self.semantic_label,
            'zone_id': self.zone_id,
            'embedding_dim': len(self.image_embedding) if self.image_embedding else 0
        }

@dataclass
class GraphEdge:
    """Edge between nodes"""
    from_node: int
    to_node: int
    weight: float  # traversal cost (distance or time)
    traversable: bool = True
    cleaning_compatible: List[str] = None  # modes allowed on this edge
    
    def __post_init__(self):
        if self.cleaning_compatible is None:
            self.cleaning_compatible = ["sweep", "vacuum", "scrub"]

# ============================================================================
# COMPONENT 1: SIMPLIFIED PERCEPTION & MAPPING PIPELINE
# ============================================================================

class DemoTourProcessor:
    """
    Processes demo tour video to extract keyframes and build spatial structure.
    Simplified version using frame sampling instead of full SfM.
    """
    
    def __init__(self, frame_sample_rate: float = 0.5):
        """
        Args:
            frame_sample_rate: Keyframes per second to extract
        """
        self.frame_sample_rate = frame_sample_rate
        self.keyframes = []
        
    def process_video(self, video_path: str, trajectory: List[Pose2D] = None) -> List[Dict]:
        """
        Simulate video processing. In real implementation, would use:
        - OpenCV for frame extraction
        - CLIP for image embeddings
        - Visual odometry or manual annotations for poses
        
        Args:
            video_path: Path to demo tour video
            trajectory: Optional list of poses (from GPS, manual annotation, or VO)
            
        Returns:
            List of keyframe dictionaries
        """
        print(f"[DemoTourProcessor] Processing video: {video_path}")
        
        # Simulate: Extract frames at sample rate
        # Real: cv2.VideoCapture, frame extraction
        video_duration = 120  # assume 2-minute tour
        num_frames = int(video_duration * self.frame_sample_rate)
        
        keyframes = []
        for i in range(num_frames):
            # Simulate keyframe data
            if trajectory and i < len(trajectory):
                pose = trajectory[i]
            else:
                # Generate synthetic trajectory (straight line + turns)
                t = i / num_frames
                x = t * 50  # 50 meters total
                y = 5 * np.sin(2 * np.pi * t * 2)  # sinusoidal path
                theta = np.arctan2(np.cos(2 * np.pi * t * 2), 1)
                pose = Pose2D(x, y, theta)
            
            # Simulate CLIP embedding (512-dim vector)
            # Real: clip_model.encode_image(frame)
            embedding = np.random.randn(512).tolist()
            
            keyframe = {
                'frame_id': i,
                'timestamp': i / self.frame_sample_rate,
                'pose': pose,
                'embedding': embedding,
                'image_path': f"frame_{i:04d}.jpg"  # would be real path
            }
            keyframes.append(keyframe)
        
        self.keyframes = keyframes
        print(f"[DemoTourProcessor] Extracted {len(keyframes)} keyframes")
        return keyframes


class TopologicalGraphBuilder:
    """
    Builds topological graph from keyframes.
    Uses spatial proximity and visual similarity.
    """
    
    def __init__(self, 
                 distance_threshold: float = 5.0,
                 min_nodes: int = 20):
        """
        Args:
            distance_threshold: Max distance between connected nodes (meters)
            min_nodes: Minimum nodes to create in graph
        """
        self.distance_threshold = distance_threshold
        self.min_nodes = min_nodes
        self.nodes = []
        self.edges = []
        
    def build_graph(self, keyframes: List[Dict], zone_labels: Dict[int, str] = None) -> 'TopologicalGraph':
        """
        Build topological graph from keyframes.
        
        Args:
            keyframes: Output from DemoTourProcessor
            zone_labels: Optional mapping of frame_id -> zone_name
            
        Returns:
            TopologicalGraph object
        """
        print(f"[GraphBuilder] Building graph from {len(keyframes)} keyframes")
        
        # Step 1: Sample nodes from keyframes (subsample for graph sparsity)
        sample_interval = max(1, len(keyframes) // self.min_nodes)
        sampled_frames = keyframes[::sample_interval]
        
        # Step 2: Create nodes
        nodes = []
        for i, frame in enumerate(sampled_frames):
            zone = zone_labels.get(frame['frame_id']) if zone_labels else None
            node = GraphNode(
                id=i,
                pose=frame['pose'],
                semantic_label=f"Location_{i}",
                zone_id=zone,
                image_embedding=frame['embedding'][:64]  # truncate for demo
            )
            nodes.append(node)
        
        # Step 3: Create edges based on spatial proximity
        edges = []
        for i, node_i in enumerate(nodes):
            for j, node_j in enumerate(nodes):
                if i >= j:
                    continue
                    
                dist = node_i.pose.distance_to(node_j.pose)
                
                # Connect nearby nodes
                if dist < self.distance_threshold:
                    edge = GraphEdge(
                        from_node=i,
                        to_node=j,
                        weight=dist,
                        traversable=True
                    )
                    edges.append(edge)
                    
                    # Also add reverse edge (undirected graph)
                    edge_reverse = GraphEdge(
                        from_node=j,
                        to_node=i,
                        weight=dist,
                        traversable=True
                    )
                    edges.append(edge_reverse)
        
        # Step 4: Ensure graph connectivity (add edges to nearest neighbor if isolated)
        adjacency = defaultdict(list)
        for edge in edges:
            adjacency[edge.from_node].append(edge.to_node)
        
        for i, node in enumerate(nodes):
            if i not in adjacency or len(adjacency[i]) == 0:
                # Find nearest node
                min_dist = float('inf')
                nearest = None
                for j, other in enumerate(nodes):
                    if i == j:
                        continue
                    dist = node.pose.distance_to(other.pose)
                    if dist < min_dist:
                        min_dist = dist
                        nearest = j
                
                if nearest is not None:
                    edges.append(GraphEdge(i, nearest, min_dist, True))
                    edges.append(GraphEdge(nearest, i, min_dist, True))
        
        print(f"[GraphBuilder] Created {len(nodes)} nodes, {len(edges)} edges")
        
        # Step 5: Create graph object
        graph = TopologicalGraph(nodes, edges)
        return graph


class TopologicalGraph:
    """
    Topological graph data structure with spatial indexing.
    """
    
    def __init__(self, nodes: List[GraphNode], edges: List[GraphEdge]):
        self.nodes = {node.id: node for node in nodes}
        self.edges = edges
        
        # Build adjacency list for fast lookup
        self.adjacency = defaultdict(list)
        for edge in edges:
            self.adjacency[edge.from_node].append({
                'to': edge.to_node,
                'weight': edge.weight,
                'traversable': edge.traversable
            })
    
    def get_node(self, node_id: int) -> Optional[GraphNode]:
        """Get node by ID"""
        return self.nodes.get(node_id)
    
    def get_neighbors(self, node_id: int) -> List[Dict]:
        """Get neighbors of a node"""
        return self.adjacency[node_id]
    
    def find_nearest_node(self, pose: Pose2D) -> int:
        """Find nearest node to a given pose"""
        min_dist = float('inf')
        nearest = None
        for node_id, node in self.nodes.items():
            dist = node.pose.distance_to(pose)
            if dist < min_dist:
                min_dist = dist
                nearest = node_id
        return nearest
    
    def save(self, filepath: str):
        """Save graph to JSON file"""
        data = {
            'nodes': [node.to_dict() for node in self.nodes.values()],
            'edges': [asdict(edge) for edge in self.edges]
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"[Graph] Saved to {filepath}")
    
    def visualize_ascii(self):
        """Simple ASCII visualization of graph structure"""
        print("\n[Graph Visualization]")
        print(f"Nodes: {len(self.nodes)}")
        print(f"Edges: {len(self.edges)}")
        print("\nNode Positions:")
        for node_id, node in sorted(self.nodes.items())[:10]:  # show first 10
            print(f"  Node {node_id}: ({node.pose.x:.1f}, {node.pose.y:.1f}) - {node.zone_id or 'no zone'}")
        print(f"  ... ({len(self.nodes) - 10} more nodes)" if len(self.nodes) > 10 else "")
        
        print("\nConnectivity Sample:")
        for node_id in list(self.adjacency.keys())[:5]:
            neighbors = [n['to'] for n in self.adjacency[node_id]]
            print(f"  Node {node_id} -> {neighbors}")


# ============================================================================
# COMPONENT 2: NAVIGATION PLANNER OVER GRAPH
# ============================================================================

@dataclass
class PathPlan:
    """Represents a planned path"""
    node_sequence: List[int]
    waypoints: List[Pose2D]
    total_distance: float
    estimated_time: float  # seconds
    
    def __str__(self):
        return (f"PathPlan(nodes={len(self.node_sequence)}, "
                f"distance={self.total_distance:.2f}m, "
                f"time={self.estimated_time:.1f}s)")


class AStarPlanner:
    """
    A* path planner on topological graph.
    """
    
    def __init__(self, graph: TopologicalGraph, robot_speed: float = 0.5):
        """
        Args:
            graph: Topological graph to plan on
            robot_speed: Robot speed in m/s
        """
        self.graph = graph
        self.robot_speed = robot_speed
    
    def plan(self, start_node: int, goal_node: int) -> Optional[PathPlan]:
        """
        Plan path from start to goal using A*.
        
        Args:
            start_node: Starting node ID
            goal_node: Goal node ID
            
        Returns:
            PathPlan or None if no path exists
        """
        if start_node not in self.graph.nodes or goal_node not in self.graph.nodes:
            print(f"[Planner] Invalid start or goal node")
            return None
        
        # A* implementation
        open_set = [(0, start_node)]  # (f_score, node)
        came_from = {}
        g_score = {start_node: 0}
        
        goal_pose = self.graph.nodes[goal_node].pose
        
        while open_set:
            _, current = heapq.heappop(open_set)
            
            if current == goal_node:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start_node)
                path.reverse()
                
                return self._build_path_plan(path)
            
            # Explore neighbors
            for neighbor_info in self.graph.get_neighbors(current):
                neighbor = neighbor_info['to']
                if not neighbor_info['traversable']:
                    continue
                
                tentative_g = g_score[current] + neighbor_info['weight']
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    
                    # Heuristic: Euclidean distance to goal
                    h = self.graph.nodes[neighbor].pose.distance_to(goal_pose)
                    f = tentative_g + h
                    
                    heapq.heappush(open_set, (f, neighbor))
        
        print(f"[Planner] No path found from {start_node} to {goal_node}")
        return None
    
    def _build_path_plan(self, node_sequence: List[int]) -> PathPlan:
        """Build PathPlan object from node sequence"""
        waypoints = [self.graph.nodes[nid].pose for nid in node_sequence]
        
        # Calculate total distance
        total_distance = 0
        for i in range(len(waypoints) - 1):
            total_distance += waypoints[i].distance_to(waypoints[i+1])
        
        estimated_time = total_distance / self.robot_speed
        
        return PathPlan(
            node_sequence=node_sequence,
            waypoints=waypoints,
            total_distance=total_distance,
            estimated_time=estimated_time
        )


class MultiGoalPlanner:
    """
    Plans paths through multiple goals (TSP-like problem).
    Uses greedy nearest-neighbor for demo (optimal TSP is NP-hard).
    """
    
    def __init__(self, graph: TopologicalGraph, planner: AStarPlanner):
        self.graph = graph
        self.planner = planner
    
    def plan_multi_goal(self, start_node: int, goal_nodes: List[int]) -> Optional[PathPlan]:
        """
        Plan path visiting all goals.
        
        Args:
            start_node: Starting node
            goal_nodes: List of goal nodes to visit
            
        Returns:
            PathPlan visiting all goals
        """
        if not goal_nodes:
            return None
        
        # Greedy nearest-neighbor heuristic
        current = start_node
        remaining = set(goal_nodes)
        full_path = [start_node]
        total_distance = 0
        
        while remaining:
            # Find nearest unvisited goal
            best_goal = None
            best_dist = float('inf')
            best_subpath = None
            
            for goal in remaining:
                subpath = self.planner.plan(current, goal)
                if subpath and subpath.total_distance < best_dist:
                    best_dist = subpath.total_distance
                    best_goal = goal
                    best_subpath = subpath
            
            if best_goal is None:
                print(f"[MultiGoalPlanner] Cannot reach remaining goals")
                break
            
            # Add to path (skip first node to avoid duplicates)
            full_path.extend(best_subpath.node_sequence[1:])
            total_distance += best_subpath.total_distance
            current = best_goal
            remaining.remove(best_goal)
        
        # Build final path plan
        waypoints = [self.graph.nodes[nid].pose for nid in full_path]
        estimated_time = total_distance / self.planner.robot_speed
        
        return PathPlan(
            node_sequence=full_path,
            waypoints=waypoints,
            total_distance=total_distance,
            estimated_time=estimated_time
        )


# ============================================================================
# DEMO / TEST
# ============================================================================

def demo_pipeline():
    """
    Demonstrates the complete perception + planning pipeline.
    """
    print("=" * 70)
    print("KINETI-TEC CHALLENGE - PART B DEMONSTRATION")
    print("=" * 70)
    
    # Step 1: Process demo tour video
    print("\n[STEP 1] Processing Demo Tour Video")
    print("-" * 70)
    processor = DemoTourProcessor(frame_sample_rate=1.0)  # 1 frame/sec
    keyframes = processor.process_video("demo_tour.mp4")
    
    # Step 2: Build topological graph
    print("\n[STEP 2] Building Topological Graph")
    print("-" * 70)
    
    # Simulate zone labels (in real system, from VLM or manual annotation)
    zone_labels = {}
    for i, frame in enumerate(keyframes):
        if i < 20:
            zone_labels[i] = "lobby"
        elif i < 50:
            zone_labels[i] = "hallway_1"
        elif i < 80:
            zone_labels[i] = "office_area"
        else:
            zone_labels[i] = "hallway_2"
    
    builder = TopologicalGraphBuilder(distance_threshold=8.0, min_nodes=30)
    graph = builder.build_graph(keyframes, zone_labels)
    
    # Visualize graph
    graph.visualize_ascii()
    
    # Save graph
    graph.save("topological_graph.json")
    
    # Step 3: Navigation Planning
    print("\n[STEP 3] Navigation Planning")
    print("-" * 70)
    
    planner = AStarPlanner(graph, robot_speed=0.5)
    
    # Example 1: Single goal navigation
    print("\nExample 1: Navigate from Node 0 to Node 25")
    path1 = planner.plan(start_node=0, goal_node=25)
    if path1:
        print(f"  {path1}")
        print(f"  Path: {' -> '.join(map(str, path1.node_sequence[:10]))}...")
    
    # Example 2: Multi-goal navigation (cleaning multiple spots)
    print("\nExample 2: Visit multiple cleaning locations")
    multi_planner = MultiGoalPlanner(graph, planner)
    goals = [5, 15, 25, 30]  # Simulated stain locations
    path2 = multi_planner.plan_multi_goal(start_node=0, goal_nodes=goals)
    if path2:
        print(f"  {path2}")
        print(f"  Visiting nodes: {path2.node_sequence}")
    
    # Step 4: Simulate robot localization and re-planning
    print("\n[STEP 4] Dynamic Re-Planning (Robot at arbitrary position)")
    print("-" * 70)
    
    # Robot is at some arbitrary position
    robot_pose = Pose2D(x=15.0, y=2.0, theta=0.5)
    nearest_node = graph.find_nearest_node(robot_pose)
    print(f"  Robot at ({robot_pose.x:.1f}, {robot_pose.y:.1f})")
    print(f"  Nearest graph node: {nearest_node}")
    
    # Re-plan to new goal
    new_goal = 28
    path3 = planner.plan(start_node=nearest_node, goal_node=new_goal)
    if path3:
        print(f"  New path: {path3}")
    
    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print("\nKey Outputs:")
    print("  1. Topological graph built from demo tour")
    print("  2. A* planner functional on graph")
    print("  3. Multi-goal planning demonstrated")
    print("  4. Dynamic localization and re-planning shown")
    print("\nNext Steps for Full Implementation:")
    print("  - Integrate real CLIP embeddings for visual place recognition")
    print("  - Add VLM for goal frame retrieval from natural language")
    print("  - Connect to OEM robot drivers for execution")
    print("  - Implement cleaning behaviors triggered at waypoints")


if __name__ == "__main__":
    demo_pipeline()