import React, { useState, useEffect } from 'react';
import { Play, MapPin, Target, Zap, Info } from 'lucide-react';

// Simplified graph data structure
const generateSampleGraph = () => {
  const nodes = [];
  const edges = [];
  const zones = ['lobby', 'hallway_1', 'office_area', 'hallway_2', 'restroom'];
  
  // Generate nodes in a realistic facility layout
  for (let i = 0; i < 40; i++) {
    const t = i / 40;
    const x = 50 + t * 600;
    const y = 200 + 100 * Math.sin(2 * Math.PI * t * 2);
    
    let zone = zones[0];
    if (i < 8) zone = 'lobby';
    else if (i < 18) zone = 'hallway_1';
    else if (i < 28) zone = 'office_area';
    else if (i < 35) zone = 'hallway_2';
    else zone = 'restroom';
    
    nodes.push({
      id: i,
      x,
      y,
      zone,
      label: `N${i}`
    });
  }
  
  // Connect nearby nodes
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const dx = nodes[i].x - nodes[j].x;
      const dy = nodes[i].y - nodes[j].y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      
      if (dist < 100) {
        edges.push({
          from: i,
          to: j,
          weight: dist
        });
      }
    }
  }
  
  return { nodes, edges };
};

// A* pathfinding implementation
const astar = (graph, start, goal) => {
  const { nodes, edges } = graph;
  const openSet = new Set([start]);
  const cameFrom = new Map();
  const gScore = new Map();
  const fScore = new Map();
  
  gScore.set(start, 0);
  fScore.set(start, heuristic(nodes[start], nodes[goal]));
  
  while (openSet.size > 0) {
    let current = Array.from(openSet).reduce((a, b) => 
      fScore.get(a) < fScore.get(b) ? a : b
    );
    
    if (current === goal) {
      return reconstructPath(cameFrom, current);
    }
    
    openSet.delete(current);
    
    const neighbors = edges
      .filter(e => e.from === current || e.to === current)
      .map(e => e.from === current ? e.to : e.from);
    
    for (const neighbor of neighbors) {
      const edge = edges.find(e => 
        (e.from === current && e.to === neighbor) ||
        (e.to === current && e.from === neighbor)
      );
      
      const tentativeG = gScore.get(current) + edge.weight;
      
      if (!gScore.has(neighbor) || tentativeG < gScore.get(neighbor)) {
        cameFrom.set(neighbor, current);
        gScore.set(neighbor, tentativeG);
        fScore.set(neighbor, tentativeG + heuristic(nodes[neighbor], nodes[goal]));
        openSet.add(neighbor);
      }
    }
  }
  
  return null;
};

const heuristic = (a, b) => {
  const dx = a.x - b.x;
  const dy = a.y - b.y;
  return Math.sqrt(dx * dx + dy * dy);
};

const reconstructPath = (cameFrom, current) => {
  const path = [current];
  while (cameFrom.has(current)) {
    current = cameFrom.get(current);
    path.unshift(current);
  }
  return path;
};

const PathPlannerDemo = () => {
  const [graph, setGraph] = useState(generateSampleGraph());
  const [startNode, setStartNode] = useState(0);
  const [goalNode, setGoalNode] = useState(25);
  const [multiGoals, setMultiGoals] = useState([10, 20, 30]);
  const [currentPath, setCurrentPath] = useState([]);
  const [mode, setMode] = useState('single'); // 'single' or 'multi'
  const [animating, setAnimating] = useState(false);
  const [robotPos, setRobotPos] = useState(0);
  
  const zoneColors = {
    lobby: '#3b82f6',
    hallway_1: '#8b5cf6',
    office_area: '#10b981',
    hallway_2: '#f59e0b',
    restroom: '#ef4444'
  };
  
  const calculatePath = () => {
    if (mode === 'single') {
      const path = astar(graph, startNode, goalNode);
      setCurrentPath(path || []);
    } else {
      // Multi-goal: greedy nearest neighbor
      let current = startNode;
      let remaining = new Set(multiGoals);
      let fullPath = [startNode];
      
      while (remaining.size > 0) {
        let bestGoal = null;
        let bestPath = null;
        let bestDist = Infinity;
        
        for (const goal of remaining) {
          const path = astar(graph, current, goal);
          if (path) {
            const dist = calculatePathDistance(path);
            if (dist < bestDist) {
              bestDist = dist;
              bestGoal = goal;
              bestPath = path;
            }
          }
        }
        
        if (!bestGoal) break;
        
        fullPath = [...fullPath, ...bestPath.slice(1)];
        current = bestGoal;
        remaining.delete(bestGoal);
      }
      
      setCurrentPath(fullPath);
    }
  };
  
  const calculatePathDistance = (path) => {
    let dist = 0;
    for (let i = 0; i < path.length - 1; i++) {
      const n1 = graph.nodes[path[i]];
      const n2 = graph.nodes[path[i + 1]];
      dist += heuristic(n1, n2);
    }
    return dist;
  };
  
  const animatePath = () => {
    if (currentPath.length === 0) return;
    
    setAnimating(true);
    setRobotPos(0);
    
    let pos = 0;
    const interval = setInterval(() => {
      pos++;
      if (pos >= currentPath.length) {
        clearInterval(interval);
        setAnimating(false);
        pos = currentPath.length - 1;
      }
      setRobotPos(pos);
    }, 300);
  };
  
  useEffect(() => {
    calculatePath();
  }, [startNode, goalNode, multiGoals, mode]);
  
  const pathDistance = currentPath.length > 0 ? calculatePathDistance(currentPath).toFixed(1) : 0;
  const estimatedTime = (pathDistance / 50).toFixed(1); // Assuming 50 px/s robot speed
  
  return (
    <div className="w-full h-screen bg-gradient-to-br from-gray-900 to-gray-800 text-white p-6">
      <div className="max-w-7xl mx-auto h-full flex flex-col">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
            <Zap className="text-yellow-400" />
            Topological Graph Navigation Planner
          </h1>
          <p className="text-gray-400">Part B: Interactive demonstration of perception mapping & A* planning</p>
        </div>
        
        {/* Control Panel */}
        <div className="bg-gray-800 rounded-lg p-4 mb-4 border border-gray-700">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Planning Mode</label>
              <select 
                value={mode}
                onChange={(e) => setMode(e.target.value)}
                className="w-full bg-gray-700 rounded px-3 py-2 border border-gray-600"
              >
                <option value="single">Single Goal</option>
                <option value="multi">Multi-Goal (TSP)</option>
              </select>
            </div>
            
            {mode === 'single' ? (
              <>
                <div>
                  <label className="block text-sm font-medium mb-2">Start Node</label>
                  <input 
                    type="number" 
                    value={startNode}
                    onChange={(e) => setStartNode(parseInt(e.target.value))}
                    min={0}
                    max={graph.nodes.length - 1}
                    className="w-full bg-gray-700 rounded px-3 py-2 border border-gray-600"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Goal Node</label>
                  <input 
                    type="number" 
                    value={goalNode}
                    onChange={(e) => setGoalNode(parseInt(e.target.value))}
                    min={0}
                    max={graph.nodes.length - 1}
                    className="w-full bg-gray-700 rounded px-3 py-2 border border-gray-600"
                  />
                </div>
              </>
            ) : (
              <div className="col-span-2">
                <label className="block text-sm font-medium mb-2">Goal Nodes (comma-separated)</label>
                <input 
                  type="text" 
                  value={multiGoals.join(', ')}
                  onChange={(e) => {
                    const goals = e.target.value.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n));
                    setMultiGoals(goals);
                  }}
                  className="w-full bg-gray-700 rounded px-3 py-2 border border-gray-600"
                  placeholder="10, 20, 30"
                />
              </div>
            )}
            
            <div className="flex items-end">
              <button
                onClick={animatePath}
                disabled={animating || currentPath.length === 0}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded px-4 py-2 flex items-center justify-center gap-2 transition-colors"
              >
                <Play size={16} />
                Animate Robot
              </button>
            </div>
          </div>
          
          {/* Stats */}
          <div className="mt-4 grid grid-cols-4 gap-4 text-center">
            <div className="bg-gray-700 rounded p-3">
              <div className="text-2xl font-bold text-blue-400">{graph.nodes.length}</div>
              <div className="text-xs text-gray-400">Graph Nodes</div>
            </div>
            <div className="bg-gray-700 rounded p-3">
              <div className="text-2xl font-bold text-purple-400">{graph.edges.length}</div>
              <div className="text-xs text-gray-400">Edges</div>
            </div>
            <div className="bg-gray-700 rounded p-3">
              <div className="text-2xl font-bold text-green-400">{pathDistance}px</div>
              <div className="text-xs text-gray-400">Path Distance</div>
            </div>
            <div className="bg-gray-700 rounded p-3">
              <div className="text-2xl font-bold text-yellow-400">{estimatedTime}s</div>
              <div className="text-xs text-gray-400">Est. Time</div>
            </div>
          </div>
        </div>
        
        {/* Graph Visualization */}
        <div className="flex-1 bg-gray-800 rounded-lg border border-gray-700 overflow-hidden relative">
          <svg className="w-full h-full">
            {/* Edges */}
            {graph.edges.map((edge, i) => {
              const n1 = graph.nodes[edge.from];
              const n2 = graph.nodes[edge.to];
              const isInPath = currentPath.includes(edge.from) && currentPath.includes(edge.to) &&
                Math.abs(currentPath.indexOf(edge.from) - currentPath.indexOf(edge.to)) === 1;
              
              return (
                <line
                  key={i}
                  x1={n1.x}
                  y1={n1.y}
                  x2={n2.x}
                  y2={n2.y}
                  stroke={isInPath ? '#10b981' : '#374151'}
                  strokeWidth={isInPath ? 3 : 1}
                  opacity={isInPath ? 1 : 0.3}
                />
              );
            })}
            
            {/* Nodes */}
            {graph.nodes.map((node) => {
              const isStart = node.id === startNode;
              const isGoal = mode === 'single' ? node.id === goalNode : multiGoals.includes(node.id);
              const isInPath = currentPath.includes(node.id);
              const isRobotPos = animating && currentPath[robotPos] === node.id;
              
              return (
                <g key={node.id}>
                  <circle
                    cx={node.x}
                    cy={node.y}
                    r={isRobotPos ? 12 : (isStart || isGoal) ? 8 : 5}
                    fill={isRobotPos ? '#ef4444' : isStart ? '#3b82f6' : isGoal ? '#f59e0b' : zoneColors[node.zone]}
                    stroke={isInPath ? '#10b981' : 'none'}
                    strokeWidth={2}
                    opacity={isInPath || isStart || isGoal || isRobotPos ? 1 : 0.5}
                  />
                  {(isStart || isGoal || isRobotPos) && (
                    <text
                      x={node.x}
                      y={node.y - 15}
                      textAnchor="middle"
                      fill="white"
                      fontSize="10"
                      fontWeight="bold"
                    >
                      {isRobotPos ? '🤖' : isStart ? 'START' : 'GOAL'}
                    </text>
                  )}
                </g>
              );
            })}
            
            {/* Path direction arrows */}
            {currentPath.length > 1 && currentPath.slice(0, -1).map((nodeId, i) => {
              const n1 = graph.nodes[nodeId];
              const n2 = graph.nodes[currentPath[i + 1]];
              const midX = (n1.x + n2.x) / 2;
              const midY = (n1.y + n2.y) / 2;
              const angle = Math.atan2(n2.y - n1.y, n2.x - n1.x) * 180 / Math.PI;
              
              return (
                <polygon
                  key={`arrow-${i}`}
                  points="0,-4 8,0 0,4"
                  fill="#10b981"
                  transform={`translate(${midX},${midY}) rotate(${angle})`}
                  opacity={0.8}
                />
              );
            })}
          </svg>
          
          {/* Legend */}
          <div className="absolute top-4 right-4 bg-gray-900 bg-opacity-90 rounded p-3 text-xs">
            <div className="font-bold mb-2 flex items-center gap-2">
              <Info size={14} />
              Zone Legend
            </div>
            {Object.entries(zoneColors).map(([zone, color]) => (
              <div key={zone} className="flex items-center gap-2 mb-1">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }}></div>
                <span className="capitalize">{zone.replace('_', ' ')}</span>
              </div>
            ))}
          </div>
        </div>
        
        {/* Path Info */}
        {currentPath.length > 0 && (
          <div className="mt-4 bg-gray-800 rounded-lg p-4 border border-gray-700">
            <h3 className="font-bold mb-2">Computed Path ({currentPath.length} nodes)</h3>
            <div className="text-sm text-gray-400 font-mono">
              {currentPath.map((n, i) => (
                <span key={i}>
                  Node {n}
                  {i < currentPath.length - 1 && ' → '}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PathPlannerDemo;