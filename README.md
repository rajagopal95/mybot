# 🤖 MyBot — ROS2 SLAM Comparative Study & Navigation Stack

A ROS2 workspace for autonomous mobile robot (AMR) simulation, mapping, localization, and navigation — built around a **comparative SLAM study** (SLAM Toolbox vs Cartographer vs RTAB-Map) with a full Nav2 navigation pipeline.

The workspace is developed and tested using **ROS2 Humble on Ubuntu 22.04**.

---

# 📌 Overview

`mybot_ws` simulates a differential-drive robot in Gazebo and supports three interchangeable SLAM backends, letting you map the same environment multiple ways and compare results before moving into autonomous navigation with Nav2.

The workspace contains:

- Robot description (URDF/Xacro)
- Gazebo simulation worlds
- Three SLAM backends (SLAM Toolbox, Cartographer, RTAB-Map)
- Nav2-based navigation with EKF-fused odometry
- Interactive map-saving script
- Shell scripts for one-command mapping, navigation, verification, and cleanup

---

# 🚀 Features

- 🤖 Autonomous Mobile Robot (AMR) simulation
- 🗺️ Multiple SLAM algorithms — SLAM Toolbox, Cartographer, RTAB-Map
- 🚀 ROS2 Nav2 navigation stack
- 📍 Localization with initial pose estimation
- 🌍 Gazebo simulation
- 📊 RViz visualization
- 💾 Interactive map-saving script
- 📄 Log generation
- 🛠️ One-command mapping / navigation / verify / kill scripts

---

# 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Operating System | Ubuntu 22.04 |
| Middleware | ROS2 Humble |
| Programming | Python |
| SLAM | slam_toolbox, Cartographer, RTAB-Map |
| Navigation | ROS2 Navigation Stack (Nav2) |
| Sensor Fusion | robot_localization (EKF) |
| Visualization | RViz2 |
| Simulation | Gazebo Classic |
| Build System | Colcon |

---

# 📂 Project Structure

```text
mybot_ws/
└── src/
    └── mybot/
        ├── mybot_description/     # URDF/Xacro robot model
        ├── mybot_gazebo/          # Gazebo worlds + launch + controllers
        ├── mybot_navigation/      # Nav2 launch, params, EKF, RViz config
        ├── mybot_rtabmap/         # RTAB-Map launch package
        ├── mybot_slam/            # SLAM Toolbox + Cartographer
        │   ├── config/
        │   ├── launch/
        │   ├── maps/
        │   ├── rviz/
        │   └── scripts/
        │       └── save_map.py
        ├── logs/
        ├── mapping.sh
        ├── start.sh
        ├── verify.sh
        ├── kill.sh
        └── README.md
```

---

# ⚙️ Installation

## Prerequisites

- Ubuntu 22.04
- ROS2 Humble
- Nav2
- Gazebo
- RViz2
- SLAM Toolbox
- Cartographer
- RTAB-Map
- robot_localization

Install required ROS2 packages:

```bash
sudo apt update

sudo apt install \
ros-humble-slam-toolbox \
ros-humble-cartographer \
ros-humble-cartographer-ros \
ros-humble-rtabmap-ros \
ros-humble-navigation2 \
ros-humble-nav2-bringup \
ros-humble-robot-localization \
ros-humble-teleop-twist-keyboard \
ros-humble-rviz2
```

---

# 📥 Clone the Repository

```bash
git clone https://github.com/rajagopal95/mybot_ws.git
cd mybot_ws
```

---

# 🔨 Build the Workspace

```bash
colcon build --symlink-install
source install/setup.bash
```

For every new terminal:

```bash
source ~/mybot_ws/install/setup.bash
```

---

# 🧭 Quick Start Tutorial

The full workflow revolves around four scripts: `verify.sh`, `mapping.sh`, `start.sh`, and `kill.sh`.

## 1. Verify your setup

Before your first run, confirm dependencies are installed:

```bash
bash verify.sh
```

## 2. Mapping — `mapping.sh`

```bash
bash mapping.sh
```

You'll be prompted to choose a SLAM backend:

```text
====================================
        SELECT SLAM METHOD
====================================

1. SLAM Toolbox
2. Cartographer
3. RTAB-Map

Enter your choice:
```

| Choice | Backend | Notes |
|---|---|---|
| `1` | **SLAM Toolbox** | Lightweight 2D lidar SLAM, good default |
| `2` | **Cartographer** | Pose-graph SLAM, strong loop closure on larger maps |
| `3` | **RTAB-Map** | RGB-D/visual SLAM, use for 3D or camera-based mapping |

Each choice launches Gazebo, the robot model, the selected SLAM package, and RViz. Drive the robot around until the environment is fully mapped.

### Save the map

```bash
python3 src/mybot/mybot_slam/scripts/save_map.py
```

```text
Enter map name:
hospital
```

Saved to `mybot_slam/maps/hospital.pgm` and `hospital.yaml`.

## 3. Navigation — `start.sh`

```bash
bash start.sh
```

Launches Gazebo, robot_state_publisher, localization, Nav2, and RViz using the saved map.

**In RViz:**
1. Click **2D Pose Estimate** → click + drag on the robot's actual position/heading.
2. Click **Nav2 Goal** → click + drag on the target position/heading.

## 4. Shut everything down — `kill.sh`

```bash
bash kill.sh
```

Terminates all ROS2, Gazebo, and related processes. Run this between runs (e.g. switching from SLAM Toolbox to Cartographer) to avoid leftover nodes or port conflicts.

---

## Typical Session Example

```bash
# Terminal 1
cd ~/mybot_ws && source install/setup.bash
bash verify.sh                 # sanity check

bash mapping.sh                # choose 1 / 2 / 3
# ... drive robot around, then Ctrl+C when mapping done ...
python3 src/mybot/mybot_slam/scripts/save_map.py

bash kill.sh                   # clean up before switching modes

bash start.sh                  # launch navigation with saved map
# In RViz: 2D Pose Estimate -> Nav2 Goal

bash kill.sh                   # clean up when finished
```

---

# 🧠 Complete Workflow

```text
Build Workspace
       │
       ▼
Source Workspace
       │
       ▼
Run verify.sh
       │
       ▼
Run mapping.sh
       │
       ▼
Choose Mapping Method
 ├── SLAM Toolbox
 ├── Cartographer
 └── RTAB-Map
       │
       ▼
Drive the Robot
       │
       ▼
Run save_map.py
       │
       ▼
Enter Map Name
       │
       ▼
Map Saved (.pgm + .yaml)
       │
       ▼
Run kill.sh
       │
       ▼
Run start.sh
       │
       ▼
Open RViz
       │
       ▼
2D Pose Estimate
       │
       ▼
Send Nav2 Goal
       │
       ▼
Robot Navigates Autonomously
       │
       ▼
Run kill.sh
```

---

# 🖥️ Visualizing in RViz2

## Mapping (SLAM)

While `mapping.sh` is running, RViz opens automatically with the correct config from:

```text
mybot_slam/rviz/
```

## Navigation (Nav2)

While `start.sh` is running, RViz opens automatically with the navigation config from:

```text
mybot_navigation/
```

Set the Fixed Frame to `map` and confirm `Map`, `Costmap`, `Path`, `LaserScan`, and `TF` displays are active.

---

# 📊 ROS2 Communication

Important interfaces include:

### Velocity Command
```text
/cmd_vel
```

### LiDAR / Scan
```text
/scan
```

### Odometry / TF
```text
/odom
odom → base_link (EKF-fused)
```

To inspect available topics:

```bash
ros2 topic list
```

To inspect the TF tree:

```bash
ros2 run tf2_tools view_frames
```

---

# 📁 Utility Scripts Reference

| Script | Purpose |
|---|---|
| `verify.sh` | Verifies required packages/dependencies are installed |
| `mapping.sh` | Launches mapping workflow with SLAM backend selection menu |
| `start.sh` | Starts navigation stack using the saved map |
| `kill.sh` | Terminates all running ROS2, Gazebo, and related processes |
| `save_map.py` | Interactive script to save the current map (prompts for name) |

---

# 💾 Maps & Logs

Generated maps:

```text
mybot_slam/maps/
├── hospital.yaml / .pgm
├── office.yaml / .pgm
└── warehouse.yaml / .pgm
```

Logs:

```text
logs/
├── log1/
│   ├── gazebo.log
│   └── navigation.log
└── log2/
    ├── gazebo.log
    └── navigation.log
```

---

# 📁 Recommended Git Ignore

```gitignore
# ROS2
build/
install/
log/

# Python
__pycache__/
*.pyc

# Backups
*.bak
*.backup

# IDE
.vscode/
.idea/

# OS
.DS_Store
```

---

# 📸 Results

The system is designed to demonstrate:

- ✅ Comparative SLAM study across three backends
- ✅ Real-time LiDAR/visual mapping
- ✅ Multi-planner Nav2 navigation (SmacPlanner2D, ThetaStar, NavFn)
- ✅ EKF-based sensor fusion
- ✅ Saved occupancy-grid maps
- ✅ One-command mapping/navigation/cleanup workflow

Add project screenshots here:

```text
docs/
├── mapping.png
├── navigation.png
└── rviz.png
```

```markdown
![SLAM Mapping](docs/mapping.png)
```

---

# 🔮 Future Improvements

- Dynamic obstacle avoidance
- Per-goal planner auto-selection
- Isaac ROS perception integration
- YOLOv8-based object detection node
- Improved TF tree stability across SLAM backends

---

# 🎯 Potential Applications

- 🏥 Hospital logistics simulation
- 🏢 Indoor service robots
- 🔍 SLAM algorithm benchmarking
- 🚨 Surveillance simulation

---

# 👨‍💻 Author

**N N Rajagopal**

ROS2 | Autonomous Mobile Robots | SLAM | Navigation

Portfolio: rajagopal95.github.io/Portfolio

---

# 📜 License

This project is intended for educational, research, and autonomous mobile robot development using ROS2.
