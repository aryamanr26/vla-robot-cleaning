# Vision-Language-Driven Autonomous Cleaning System

A hierarchical navigation and task reasoning framework for autonomous cleaning robots in large indoor facilities, inspired by mobility Vision-Language-Action (VLA) architectures.

## Overview

This project demonstrates a **modular, execution-ready** system for coordinating autonomous cleaning robots across semantically-structured environments. The architecture decouples high-level task reasoning from low-level execution, enabling robust multi-zone cleaning missions with failure recovery.

### Key Features

- **Topological Navigation**: Graph-based world representation with semantic zones and navigational affordances
- **Task-Level Planning**: Priority-driven zone ordering and mission scheduling
- **Failure-Aware Execution**: Dynamic replanning on edge execution failures
- **OEM-Agnostic Design**: Hardware abstraction layer supporting multiple cleaning robot platforms
- **Vision-Language Integration Ready**: Architecture designed for VLM-based instruction parsing and goal reasoning

## System Architecture

```
                Human Instruction (Text / Image / Demo Tour)
                                 ↓
┌────────────────────────────────────────────────────────────┐
│         Vision-Language Model (VLM) Layer                  │
│  • Semantic instruction grounding                          │
│  • Demo tour context understanding                         │
│  • Structured task goal generation                         │
└─────────────────┬──────────────────────────────────────────┘
                  │ Structured Task Goals (Zone IDs, Priority)
                  │
┌─────────────────▼──────────────────────────────────────────┐
│            Mission Orchestration Layer                     │
│  • Multi-zone task scheduling                              │
│  • Priority-based zone ordering                            │
└─────────────────┬──────────────────────────────────────────┘
                  │
┌─────────────────▼──────────────────────────────────────────┐
│            Navigation Planning Layer                       │
│  • A* path planning over topological graph                 │
│  • Dynamic cost adjustment                                 │
│  • Failure-aware replanning                                │
└─────────────────┬──────────────────────────────────────────┘
                  │
┌─────────────────▼──────────────────────────────────────────┐
│            Execution & Localization Layer                  │
│  • Edge-by-edge navigation execution                       │
│  • Topological state estimation                            │
│  • Skill-based motion primitives                           │
└────────────────────────────────────────────────────────────┘
```

## World Model

The environment is represented as a **directed topological graph** with:

- **Nodes**: Semantic locations (cleaning zones, concourses, facilities, service areas)
- **Edges**: Navigational affordances with typed transitions:
  - `enter_zone` / `exit_zone`
  - `follow_corridor`
  - `enter_facility` / `exit_facility`
  - `navigate_service_corridor`

Each edge includes:
- Base traversal cost
- Optional reliability score
- Execution skill mapping

## Project Structure

```
vla-robot-cleaning/
├── app/
│   └── demo_plan.py              # Main mission simulation & demo
├── planning/
│   ├── astar_planner.py          # A* pathfinding implementation
│   ├── costs.py                  # Edge cost computation & penalties
│   └── planner_interface.py     # Abstract planner interface
├── world_model/
│   └── topological_graph.json   # Environment representation
├── interactive_planner.js        # Web-based visualization (optional)
├── perception_planner.py         # Vision integration hooks
└── README.md
```

## Quick Start

### Prerequisites

```bash
pip install networkx
```

### Running a Cleaning Mission

```bash
cd vla-robot-cleaning
python -m app.demo_plan
```

This executes a full cleaning mission across a sports facility:
1. Plans optimal cleaning order across 9 court zones
2. Navigates through concourses and service areas
3. Executes edge-by-edge navigation with replanning on failures
4. Returns to dock after completion

### Example Output

```
(rob422) aryamanr26@Aryaware:~/vla-robot-cleaning$ python -m app.demo_plan

Planned cleaning order:
 - championship_court
 - courts_1_2
 - courts_3_4
 - courts_5_6
 - courts_8
 - courts_10_11
 - courts_12_13
 - courts_7
 - courts_14

=== Navigating to clean: championship_court ===
Attempting: dock → check_in
✓ Success
Attempting: check_in → concourse_west
✓ Success
Attempting: concourse_west → concourse_east
✓ Success
Attempting: concourse_east → championship_court
✓ Success
✓ Finished cleaning zone: championship_court

=== Navigating to clean: courts_1_2 ===
Attempting: championship_court → concourse_east
✓ Success
Attempting: concourse_east → concourse_west
✓ Success
Attempting: concourse_west → courts_1_2
✓ Success
✓ Finished cleaning zone: courts_1_2

...

All assigned zones cleaned. Returning to dock.
```

## 🧠 Vision-Language Model (VLM / VLA) Integration

This system incorporates **Vision-Language Models (VLMs)** as a **high-level task grounding layer**, inspired by the Mobility-VLA framework.

### Role of the VLM

VLMs are **not used for real-time navigation or control**. Instead, they are responsible for:

- Interpreting unstructured human instructions (text, image, or demo video context)
- Grounding instructions to **semantic locations or zones**
- Producing **structured task goals** that downstream planners can execute

The VLM sits *above* the task and navigation stack:

```
Human Instruction (Text / Image / Demo Tour)
                 ↓
    Vision-Language Model (VLM)
                 ↓
Structured Task Goals (Zone IDs, Priority, Cleaning Mode)
                 ↓
    Task / Zone Reasoning Module
                 ↓
  Topological Navigation Planner
                 ↓
   Execution & Failure Recovery
```

### Why the VLM Is Not in the Control Loop

Vision-Language Models are:
- Computationally expensive
- Non-deterministic
- Unsuitable for tight real-time control loops

As a result:
- VLMs run **infrequently**
- Outputs are treated as **semantic intent**, not control commands
- Classical planners handle execution and recovery

This design mirrors real-world robotics systems and avoids coupling high-latency reasoning with safety-critical motion.

### Challenge Scope Note

Due to challenge constraints (no physical robot, no onboard compute, no demo tour video), **VLM inference is stubbed** in this implementation.

However, the interfaces and data flow are explicitly designed to support direct integration with models such as **Gemini 1.5 Pro or GPT-4V**.

Downstream components (task planning, navigation, failure-aware execution) are **fully implemented and executable**.

### Example VLM Prompt & Response

#### 📌 Example VLM Prompt
```
System:
You are a cleaning robot navigation assistant. Given a demonstration tour video
of an indoor sports facility and a user instruction, identify the most relevant
cleaning zones in the environment.

User Instruction:
"Please clean the area near the main entrance where people usually spill drinks."

Demo Tour Context:
- Concourse West: high foot traffic, near main entrance
- Championship Court: adjacent to entrance, frequent events
- Courts 1–14: sports courts with varying priority
```

#### 📌 Example VLM Output (Structured)
```json
{
  "target_zones": ["concourse_west", "championship_court"],
  "cleaning_mode": "spot_clean",
  "priority": "high",
  "confidence": 0.82
}
```

#### 📌 How This Feeds the System
```python
vlm_output = {
    "target_zones": ["concourse_west", "championship_court"],
    "cleaning_mode": "spot_clean",
    "priority": "high"
}

task_list = plan_cleaning_tasks_from_vlm(vlm_output, graph)
```

The resulting task list is then executed using the existing task planner, navigation planner, and failure-aware execution loop.

### VLM Integration Justification

Vision-Language Models are used exclusively for high-level task grounding rather than real-time navigation or control. Given the lack of hardware and demo-tour data in this challenge, VLM execution is intentionally stubbed. The system instead demonstrates a fully functional downstream planning and execution stack, with clear interfaces designed for future integration of models such as Gemini or GPT-4V. This reflects real-world practice, where VLMs provide semantic intent while classical planners ensure reliable execution.

## Supported Robot Platforms

The system is designed with OEM abstraction for:

- **Pudu CC1 Pro**: VSLAM + LiDAR, AI spot detection
- **Keenon C40**: Multi-sensor fusion, compact design
- **Gausium Omnie**: 3D LiDAR, large-scale facilities

*Note: Part B implements the planning and reasoning layers. OEM-specific drivers are defined via abstraction interfaces.*

## Design Principles

### Hierarchical Decomposition
Clear separation between task reasoning (what to clean), navigation planning (how to navigate), and execution (skill-based motion).

### Execution-Aware Planning
Navigation costs dynamically adjust based on:
- Task context and zone priorities
- Environmental conditions
- Historical execution reliability
- Temporary edge failures

### Failure Recovery
Failed edge executions trigger:
1. Temporary edge penalization
2. Replanning from current state
3. Continued mission execution

No full mission resets—mimics real-world robot behavior.

### Modularity
Each component operates behind well-defined interfaces:
- World model is JSON-based and parser-agnostic
- Navigation planner is backend-swappable (NetworkX, GTSAM, etc.)
- Localization is stubbed for future vision/VLM integration

## Cleaning Behaviors (Planned)

The system architecture supports multiple cleaning primitives:

- **Coverage Path**: Full-zone cleaning with boustrophedon or spiral patterns
- **Spot Cleaning**: Targeted stain removal triggered by vision
- **Zone Perimeter**: Edge and corner cleaning
- **Adaptive Intensity**: Floor-type and dirt-level based adjustment

*Implementation planned for production deployment.*

## Vision-Language Integration (Roadmap)

The VLM layer described above enables:
- Natural language task instructions
- Demo tour video ingestion for environment understanding
- Goal frame identification from visual context
- Multi-modal instruction understanding

**Planned integration targets:**
- **Gemini 1.5 Pro** or **GPT-4V** for long-context reasoning
- **CLIP** embeddings for spatial grounding
- **SfM pipelines** (COLMAP) for offline graph construction from demo tours

*See the VLM Integration section above for architectural details and example workflows.*

## Development Timeline

- ✅ **24h MVP**: Topological planner with mock execution
- ✅ **48h Prototype**: Real navigation with failure handling
- 🚧 **Week 1**: VLM integration and demo tour pipeline
- 🚧 **Week 2-3**: Multi-robot coordination and OEM drivers
- 🚧 **Month 1**: Production deployment with field testing

## Known Limitations

This implementation focuses on **system structure and execution logic**:

- **No metric SLAM**: Uses topological abstraction
- **No low-level control**: Skill execution is simulated
- **No OEM APIs**: Hardware abstraction defined but not implemented
- **No vision pipelines**: Localization and perception are stubbed

These components are clearly separated by interfaces and can be integrated without architectural changes.

## Contributing

This is a challenge submission demonstrating autonomous cleaning robot architecture. For production deployment considerations, see `Part A: Planning & System Design` in the project documentation.

## License

MIT License - See LICENSE file for details

## Acknowledgments

Architecture inspired by:
- Mobility VLA research (demonstration-based navigation)
- Modern topological SLAM approaches
- Production cleaning robot systems (iRobot, Keenon, Pudu)

---

**Built for Kineti-Tec Robotics Olympics Challenge 01**