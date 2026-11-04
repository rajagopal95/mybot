# 🤖 MyBot — ROS2 SLAM Comparative Study & Navigation Stack

A ROS2 workspace for autonomous mobile robot (AMR) simulation, mapping, localization, and navigation — built around a **comparative SLAM study** (SLAM Toolbox vs Cartographer) with a full Nav2 navigation pipeline. It also includes a **forklift AMR** model with its own Gazebo launch file, warehouse worlds, and a Nav2 parameter set tuned for its long, narrow footprint.

The workspace is developed and tested using **ROS2 Humble on Ubuntu 22.04**.

---

# 📌 Overview

`mybot_ws` simulates differential-drive robots in Gazebo and supports two interchangeable SLAM backends, letting you map the same environment multiple ways and compare results before moving into autonomous navigation with Nav2.

The workspace contains:

- Robot descriptions (URDF/Xacro): `mybot` and a forklift AMR
- Gazebo simulation worlds (hospital, room, warehouse) and AWS warehouse models
- Two SLAM backends (SLAM Toolbox, Cartographer)
- Nav2-based navigation with EKF-fused odometry
- Footprint-aware planning (Smac Hybrid-A*) and MPPI control for the forklift
- Interactive map-saving script
- Shell scripts for one-command mapping, navigation, verification, and cleanup (`mapping.sh` and `start.sh` support both `mybot` and `forklift`)

---

# 🚀 Features

- 🤖 Autonomous Mobile Robot (AMR) simulation, including a forklift model
- 🗺️ Multiple SLAM algorithms — SLAM Toolbox, Cartographer
- 🚀 ROS2 Nav2 navigation stack (Smac Hybrid-A* + MPPI, with ThetaStar / NavFn / DWB fallbacks)
- 🚜 Polygonal forklift footprint with reverse-capable planning for tight aisles
- 📡 Ultrasonic range layer in the local costmap for obstacles below the lidar plane
- 🚧 Optional keepout zones to block specific narrow gaps
- 📍 Localization with initial pose estimation
- 🌍 Gazebo simulation with selectable worlds (hospital, room, small warehouse)
- 📊 RViz visualization
- 💾 Interactive map-saving script
- 📄 Log generation
- 🛠️ One-command mapping / navigation / verify / kill scripts
- 🩺 AMCL localization debug script (`debug_amcl.sh`)
- 🔀 Robot selection from the scripts: mybot by default, forklift with the `forklift` argument

---

# 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Operating System | Ubuntu 22.04 |
| Middleware | ROS2 Humble |
| Programming | Python |
| SLAM | slam_toolbox, Cartographer |
| Navigation | ROS2 Navigation Stack (Nav2) |
| Global planner | Smac Hybrid-A* (primary), Theta*, NavFn |
| Local controller | MPPI (primary), DWB (fallback) |
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
        ├── mybot_description/        # Robot models
        │   ├── meshes/               # STL meshes (forklift)
        │   └── urdf/
        │       ├── mybot.urdf.xacro
        │       └── fork_redesigned_urdf.xacro
        ├── mybot_gazebo/             # Gazebo worlds, models, launch, controllers
        │   ├── config/
        │   │   ├── controllers.yaml
        │   │   ├── fork_controllers.yaml
        │   │   └── fork_scan_filter.yaml
        │   ├── launch/
        │   │   ├── gazebo.launch.py
        │   │   └── fork_gazebo.launch.py
        │   ├── models/               # AWS RoboMaker warehouse models
        │   ├── scripts/
        │   └── worlds/
        │       ├── hospital.world
        │       ├── room.world
        │       ├── small_warehouse.world
        │       └── no_roof_small_warehouse.world
        ├── mybot_navigation/         # Nav2 launch, params, EKF, RViz config
        │   ├── config/
        │   │   ├── ekf.yaml
        │   │   └── nav2_params.yaml
        │   ├── launch/navigation.launch.py
        │   └── rviz/nav2.rviz
        ├── mybot_slam/               # SLAM Toolbox + Cartographer
        │   ├── config/
        │   │   ├── cartographer.lua
        │   │   ├── ekf.yaml
        │   │   ├── mapper_params_online_async.yaml
        │   │   ├── scan_filter.yaml
        │   │   └── slam_params.yaml
        │   ├── launch/
        │   │   ├── slam.launch.py
        │   │   ├── online_async_launch.py
        │   │   └── cartographer.launch.py
        │   ├── maps/
        │   ├── rviz/
        │   │   ├── slam.rviz
        │   │   └── fork_mapping.rviz
        │   └── scripts/
        │       └── save_map.py
        ├── logs/
        ├── mapping.sh
        ├── start.sh
        ├── verify.sh
        ├── debug_amcl.sh
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
- robot_localization

Install required ROS2 packages:

```bash
sudo apt update

sudo apt install \
ros-humble-slam-toolbox \
ros-humble-cartographer \
ros-humble-cartographer-ros \
ros-humble-navigation2 \
ros-humble-nav2-bringup \
ros-humble-nav2-smac-planner \
ros-humble-nav2-mppi-controller \
ros-humble-robot-localization \
ros-humble-teleop-twist-keyboard \
ros-humble-rviz2
```

The forklift launch file also uses `gazebo_ros`, `gazebo_ros2_control`, `controller_manager`, `xacro` and `laser_filters`. If any are missing:

```bash
sudo apt install \
ros-humble-gazebo-ros-pkgs \
ros-humble-gazebo-ros2-control \
ros-humble-ros2-control \
ros-humble-ros2-controllers \
ros-humble-xacro \
ros-humble-laser-filters
```

---

# 📥 Create the Workspace and Clone the Repository

First create the workspace named `mybot_ws`, with a `src` folder inside it, then clone the repo into `src`:

```bash
mkdir -p ~/mybot_ws/src
cd ~/mybot_ws/src
git clone https://github.com/rajagopal95/mybot.git 
cd ~/mybot_ws
```

The `mybot` at the end of the clone command places the repo in `~/mybot_ws/src/mybot`, which matches the project structure above.

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

If you do not build with `--symlink-install`, rebuild after every edit. Gazebo and the launch files read the installed copy, not the files in `src`.

---

# 🧭 Quick Start Tutorial

The full workflow revolves around four scripts: `verify.sh`, `mapping.sh`, `start.sh`, and `kill.sh`.

## 1. Verify your setup

Before your first run, confirm dependencies and the workspace are ready:

```bash
bash verify.sh
```

It checks the ROS 2 Humble environment, required and forklift packages, Gazebo, the built workspace packages, the helper scripts, and saved maps. Missing packages are listed with a ready-to-run `sudo apt install` command. It exits with code `1` if a required check fails.

## 2. Mapping — `mapping.sh`

```bash
bash mapping.sh             # mybot (default)
bash mapping.sh forklift    # forklift AMR
```

### Choosing the robot

By default, `mapping.sh` uses the **mybot** URDF (`mybot.urdf.xacro`). Pass `forklift` as an argument to use the forklift URDF (`fork_redesigned_urdf.xacro`) instead. The SLAM backend menu below appears in both cases.

You'll be prompted to choose a SLAM backend:

```text
====================================
        SELECT SLAM METHOD
====================================

1. SLAM Toolbox
2. Cartographer

Enter your choice:
```

| Choice | Backend | Notes |
|---|---|---|
| `1` | **SLAM Toolbox** | Lightweight 2D lidar SLAM, good default |
| `2` | **Cartographer** | Pose-graph SLAM, strong loop closure on larger maps |

Each choice launches Gazebo, the robot model, the selected SLAM package, and RViz. Drive the robot around until the environment is fully mapped.

### Save the map

```bash
ros2 run mybot_slam save_map.py
```

```text
Enter map name:
hospital
```

Saved to `mybot_slam/maps/hospital.pgm` and `hospital.yaml`.

## 3. Navigation — `start.sh`

```bash
bash start.sh               # mybot (default)
bash start.sh forklift      # forklift AMR
```

Launches Gazebo, robot_state_publisher, localization, Nav2, and RViz using the saved map. Like `mapping.sh`, `start.sh` uses the **mybot** URDF by default; pass `forklift` to navigate with the forklift URDF.

Use a map made with the same world and robot you navigate with. For example, map the warehouse with `bash mapping.sh forklift` before running `bash start.sh forklift` there.

**In RViz:**
1. Click **2D Pose Estimate** → click + drag on the robot's actual position/heading.
2. Click **Nav2 Goal** → click + drag on the target position/heading.

If the robot does not localize (no `map → odom` transform, or the pose does not update), run the AMCL checks:

```bash
bash debug_amcl.sh
```

## 4. Shut everything down — `kill.sh`

```bash
bash kill.sh
```

Terminates all ROS2, Gazebo, and related processes. Run this between runs (e.g. switching from SLAM Toolbox to Cartographer, or from mybot to forklift) to avoid leftover nodes or port conflicts.

---

## Typical Session Example

```bash
# Terminal 1
cd ~/mybot_ws && source install/setup.bash
bash verify.sh                 # sanity check

bash mapping.sh                # mybot: choose 1 / 2
# ... drive robot around, then Ctrl+C when mapping done ...
python3 src/mybot/mybot_slam/scripts/save_map.py

sudo sh kill.sh                   # clean up before switching modes

bash start.sh                  # launch navigation with saved map
# In RViz: 2D Pose Estimate -> Nav2 Goal
# If localization fails, run in another terminal: bash debug_amcl.sh

sudo sh kill.sh                   # clean up when finished
```

### Forklift variant

```bash
bash mapping.sh forklift       # forklift URDF: choose 1 / 2
# ... drive robot around, then Ctrl+C when mapping done ...
python3 src/mybot/mybot_slam/scripts/save_map.py

sudo sh kill.sh

bash start.sh forklift         # navigation with the forklift URDF
# In RViz: 2D Pose Estimate -> Nav2 Goal

sudo sh kill.sh
```

---

# 🏗️ Forklift Simulation

There are two ways to run the forklift:

- `fork_gazebo.launch.py` — simulation and teleop only (described below).
- `bash mapping.sh forklift` / `bash start.sh forklift` — the full SLAM and Nav2 workflows with the forklift URDF.

The forklift AMR has its own Gazebo launch file, `fork_gazebo.launch.py`. It starts Gazebo with the chosen world, publishes the robot description, spawns the robot as `fork_robot`, starts the `/scan` laser filter, and spawns `joint_state_broadcaster` and `diff_drive_controller` after a short delay.

```bash
cd ~/mybot_ws
source install/setup.bash
ros2 launch mybot_gazebo fork_gazebo.launch.py
```

## Launch arguments

| Argument | Default | Description |
|---|---|---|
| `world_name` | `hospital.world` | Any file in `mybot_gazebo/worlds` |
| `xacro_name` | `fork_redesigned_urdf.xacro` | Any robot xacro in `mybot_description/urdf` |
| `x_pose` | `0.0` | Spawn x position (m) |
| `y_pose` | `0.0` | Spawn y position (m) |
| `yaw_pose` | `0.0` | Spawn heading (rad) |
| `use_camera` | `false` | Compatibility argument; the forklift has no camera |

## Worlds

| World | Notes |
|---|---|
| `hospital.world` | Default world; matches the saved `hospital` map |
| `room.world` | Simple room |
| `small_warehouse.world` | AWS RoboMaker small warehouse with roof |
| `no_roof_small_warehouse.world` | Same warehouse without the roof (better view in `gzclient`) |

Example — forklift in the roofless warehouse, with a custom spawn pose:

```bash
ros2 launch mybot_gazebo fork_gazebo.launch.py \
  world_name:=no_roof_small_warehouse.world \
  x_pose:=<x> y_pose:=<y> yaw_pose:=<yaw>
```

If the robot spawns inside a shelf, choose a different `x_pose` / `y_pose` until it sits in an aisle. The saved `hospital` map only fits the hospital world, so map the warehouse again with `mapping.sh forklift` before using Nav2 there.

## Drive it

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

## Notes

- The launch file sets `GAZEBO_MODEL_PATH` and `GAZEBO_RESOURCE_PATH` itself, so no manual `export` is needed.
- Warehouse model files must use `model://<name>/...` mesh paths. A `file://models/...` path will not resolve and the mesh will not load.
- Meshes are loaded from `mybot_description/meshes` through `package://mybot_description/meshes`.
- The lift joint is passive in the current xacro; it holds position but is not actuated yet.

---

# 🧭 Forklift Nav2 Tuning

The forklift uses its own parameter set in `mybot_navigation/config/nav2_params.yaml`, tuned for warehouse aisles of 0.9 m to 1.2 m.

| Item | Setting |
|---|---|
| Footprint | Polygon matching the chassis and tapered forks: about 0.76 m wide, 0.97 m long (x from +0.05 to −0.92 m from `base_footprint`) |
| Footprint padding | `0.01` m per side in both costmaps |
| Global planner | `GridBased` = `SmacPlannerHybrid`, Reeds-Shepp motion model (can reverse), footprint-aware. `ThetaStar` and `NavFn` remain as fallbacks |
| Local controller | `FollowPath` = MPPI (DiffDrive model). `DWB` is the fallback |
| Velocity limits | Forward 0.35 m/s, reverse 0.20 m/s, rotation 0.60 rad/s |
| Local costmap | 4 m x 4 m rolling window, 0.05 m resolution, voxel layer + ultrasonic range layer + inflation |
| Global costmap | Static + obstacle + inflation layers (ultrasonics are local-only) |
| Odometry | `/odometry/filtered` everywhere (EKF-fused) |
| Scan topic | `/scan_filtered` for AMCL, costmaps |

## Inflation and footprint checking

MPPI and Smac use the full polygon footprint, not a circle. For this to run efficiently, the inflation radius must be at least half the footprint's largest dimension. With a 0.97 m long footprint, use an `inflation_radius` of about 0.55 m. Keep these values identical in three places:

- `local_costmap` → `inflation_layer`
- `global_costmap` → `inflation_layer`
- MPPI `ObstaclesCritic` (`inflation_radius` and `cost_scaling_factor`)

If the controller logs "Inflation layer either not found or inflation is not set sufficiently for optimized non-circular collision checking", the radius is too small. Collision checking then falls back to a much slower path and the controller misses its 20 Hz rate.

## Narrow gaps and keepout zones

The planner only treats a gap as blocked if the footprint would touch inscribed or lethal cells. A gap wider than the footprint plus padding (for example 0.87 m against a 0.78 m padded footprint) is therefore planned through, whatever the inflation cost. Two ways to prevent that:

1. **Keepout zone (recommended for a specific gap).** Paint the gap black on a copy of the map image, save it as a mask yaml, and enable the Nav2 keepout filter. Other aisles keep working.

   ```yaml
   local_costmap:
     local_costmap:
       ros__parameters:
         filters: ["keepout_filter"]
         keepout_filter:
           plugin: "nav2_costmap_2d::KeepoutFilter"
           enabled: True
           filter_info_topic: "/costmap_filter_info"
   # repeat for global_costmap, then run a filter mask server
   # (nav2_map_server) and costmap_filter_info_server, and add both
   # to a lifecycle manager with autostart: true
   ```

2. **Larger footprint padding.** Raising `footprint_padding` makes every gap narrower than the padded width unusable. At the default 0.01 m, padding of about 0.10 m is needed to block a 0.87 m gap, and that would also block real 0.9 m aisles.

Leave a margin of about 0.3 m around the gap entrance in the keepout mask so the robot stops before its nose reaches the inflation zone.

---

# 🩺 Troubleshooting Navigation

## Robot sits still and the goal keeps being re-sent

Typical controller log:

```text
[WARN]  Control loop missed its desired rate of 20.0000Hz   (repeated)
[ERROR] Failed to make progress
[WARN]  [follow_path] [ActionServer] Aborting handle.
```

- **"Control loop missed its desired rate"**: MPPI is too slow. Check the inflation radius (see above), then reduce `batch_size` or `time_steps`, and check CPU use with `top`, since Gazebo and Nav2 compete for CPU.
- **"Failed to make progress"** comes from `progress_checker`. With `movement_time_allowance: 15.0` it fires every 15 s while the robot is not moving. It is a symptom of the stall, not the cause.
- **Check the velocity command** while a goal is active:

  ```bash
  ros2 topic echo /cmd_vel --once
  ros2 topic echo /cmd_vel_nav --once   # if the velocity smoother remaps it
  ```

  All zeros means the controller outputs nothing. Non-zero values mean the command is not reaching the robot (remap or velocity smoother issue).
- **Swap in DWB**: name the DWB plugin `FollowPath` and send the same goal. If DWB moves the robot, the problem is MPPI load.

## Robot is too close to a wall to turn or move

The forklift's footprint reaches 0.92 m behind `base_footprint`, so a spin in place sweeps a circle of about 0.93 m radius and the Spin recovery aborts near walls. Back the robot out first:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
# or
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: -0.1}}"
```

Then clear stale cells:

```bash
ros2 service call /local_costmap/clear_entirely_local_costmap nav2_msgs/srv/ClearEntireCostmap {}
ros2 service call /global_costmap/clear_entirely_global_costmap nav2_msgs/srv/ClearEntireCostmap {}
```

For a long robot, consider a custom behavior tree (set via `default_nav_to_pose_bt_xml`) that runs `BackUp` before `Spin` in recovery.

## Useful log lines

| Message | Meaning |
|---|---|
| `Starting point in lethal space` | Planner rejected the start pose; back out and clear costmaps |
| `Optimizer fail to compute path` | MPPI found no collision-free trajectory |
| `Collision Ahead` | Spin or BackUp aborted because the swept footprint hits a cost cell |

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
Run mapping.sh  (add `forklift` for the forklift URDF)
       │
       ▼
Choose Mapping Method
 ├── SLAM Toolbox
 └── Cartographer
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
Run start.sh  (add `forklift` for the forklift URDF)
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

This folder holds `slam.rviz` and `fork_mapping.rviz`.

## Navigation (Nav2)

While `start.sh` is running, RViz opens automatically with the navigation config from:

```text
mybot_navigation/rviz/nav2.rviz
```

Set the Fixed Frame to `map` and confirm `Map`, `Costmap`, `Path`, `LaserScan`, and `TF` displays are active. The config also shows the local and global costmaps and the footprint polygon (`/global_costmap/published_footprint`), which is the quickest way to see whether the robot fits a gap.

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
/scan_filtered      (forklift launch, from the laser filter chain)
```

### Ultrasonic range sensors (forklift, local costmap)
```text
/ultrasonic_front_left   /ultrasonic_front_right
/ultrasonic_rear_left    /ultrasonic_rear_right
/ultrasonic_side_left    /ultrasonic_side_right
```

### Odometry / TF
```text
/odom
/odometry/filtered  (EKF output, used by Nav2)
odom → base_link (EKF-fused)
```

The forklift diff-drive controller publishes odometry as `odom → base_footprint`.

### Other topics (forklift)
```text
/joint_states
/imu
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
| `verify.sh` | Verifies the ROS 2 environment, required packages, built workspace, scripts, and saved maps |
| `mapping.sh [forklift]` | Launches mapping workflow with SLAM backend selection menu; uses the mybot URDF, or the forklift URDF when `forklift` is passed |
| `start.sh [forklift]` | Starts navigation stack using the saved map; uses the mybot URDF, or the forklift URDF when `forklift` is passed |
| `debug_amcl.sh` | AMCL localization debugging: node lifecycle state, initial pose publish, `/amcl_pose`, and `map → odom` TF checks |
| `kill.sh` | Terminates all running ROS2, Gazebo, and related processes |
| `save_map.py` | Interactive script to save the current map (prompts for name) |

---

# 💾 Maps & Logs

Generated maps:

```text
mybot_slam/maps/
└── hospital.yaml / .pgm
```

New maps are saved here by `save_map.py` (for example `warehouse.yaml` / `.pgm` after mapping the warehouse world). A keepout mask, if used, is a separate image and yaml saved alongside the map.

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

- ✅ Comparative SLAM study across two backends
- ✅ Real-time LiDAR mapping
- ✅ Multi-planner Nav2 navigation (Smac Hybrid-A*, ThetaStar, NavFn) with MPPI and DWB controllers
- ✅ Footprint-aware planning for the forklift, including reversing out of tight spots
- ✅ EKF-based sensor fusion
- ✅ Saved occupancy-grid maps
- ✅ One-command mapping/navigation/cleanup workflow
- ✅ Forklift AMR simulation in hospital and warehouse worlds

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
- Keepout-zone masks generated per world
- Custom recovery behavior tree (BackUp before Spin) for the forklift
- Isaac ROS perception integration
- YOLOv8-based object detection node
- Improved TF tree stability across SLAM backends
- Forklift lift actuation (position controller)
- Mapping and Nav2 navigation in the warehouse world

---

# 🎯 Potential Applications

- 🏥 Hospital logistics simulation
- 🏭 Warehouse and forklift automation simulation
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

## Third-party content

The warehouse models in `mybot_gazebo/models` (`aws_robomaker_warehouse_*`) come from the AWS RoboMaker Small Warehouse World, released under the MIT-0 license. Their mesh paths were changed from `file://models/...` to `model://...` so they load from this package.
