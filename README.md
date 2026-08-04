# MyBot ROS 2 Navigation Stack

A complete ROS 2 workspace for autonomous mobile robot (AMR) simulation, mapping, localization, and navigation. The project supports multiple SLAM algorithms and provides simple shell scripts to streamline the mapping and navigation workflow.

---

# Features

* 🤖 Autonomous Mobile Robot (AMR) simulation
* 🗺️ Multiple SLAM algorithms

  * SLAM Toolbox
  * Cartographer
  * RTAB-Map
* 🚀 ROS 2 Nav2 Navigation Stack
* 📍 Localization with Initial Pose Estimation
* 🌍 Gazebo Simulation
* 📊 RViz Visualization
* 💾 Interactive Map Saving Script
* 📁 Organized project structure
* 📄 Log generation
* 🛠️ Utility scripts for launching and verification

---

# Repository Structure

```text
mybot_ws/
└── src/
    └── mybot/
        ├── mybot_description/
        ├── mybot_gazebo/
        ├── mybot_navigation/
        ├── mybot_rtabmap/
        ├── mybot_slam/
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

# Packages

## mybot_description

Contains the robot description files.

* URDF/Xacro
* Robot model

---

## mybot_gazebo

Simulation package containing:

* Gazebo launch files
* World files
* Controller configuration

---

## mybot_navigation

Navigation package based on Nav2.

Contains:

* Navigation launch files
* Nav2 parameters
* EKF configuration
* RViz configuration

---

## mybot_slam

Contains mapping configurations and launch files for:

* SLAM Toolbox
* Cartographer

Also includes:

* SLAM configuration files
* Existing maps
* RViz configuration
* Map saving script

---

## mybot_rtabmap

Launch package for RTAB-Map based mapping.

---

# Requirements

* Ubuntu 22.04
* ROS 2 Humble
* Nav2
* Gazebo
* RViz2
* SLAM Toolbox
* Cartographer
* RTAB-Map
* robot_localization

---

# Build the Workspace

```bash
cd ~/mybot_ws

colcon build --symlink-install

source install/setup.bash
```

---

# Mapping

Start the mapping workflow by running:

```bash
bash mapping.sh
```

The script displays the following menu:

```text
====================================
        SELECT SLAM METHOD
====================================

1. SLAM Toolbox

2. Cartographer

3. RTAB-Map

Enter your choice:
```

Select the desired mapping algorithm.

After selecting a method, the script automatically launches:

* Gazebo
* Robot model
* Selected SLAM package
* RViz

Drive the robot around the environment until the entire area has been mapped.

---

# Saving the Map

Once mapping is complete, save the generated map using the provided Python script.

Run:

```bash
python3 ~/mybot_ws/src/mybot/mybot_slam/scripts/save_map.py
```

The script prompts for a map name.

Example:

```text
Enter map name:
hospital
```

The script automatically generates:

```text
mybot_slam/maps/

hospital.pgm
hospital.yaml
```

No additional arguments are required.

---

# Navigation

After a map has been created, launch the navigation stack:

```bash
bash start.sh
```

This launches:

* Gazebo
* Robot State Publisher
* Localization
* Nav2
* RViz

---

# Initial Pose Estimation

Before sending any navigation goal, the robot must be localized.

In RViz:

1. Click **2D Pose Estimate**
2. Click on the robot's current position.
3. Drag the arrow to match the robot's orientation.
4. Release the mouse.

This initializes the robot's position on the map.

> **Note:** Navigation will not work correctly until the initial pose has been set.

---

# Sending Navigation Goals

After setting the initial pose:

1. Click **Nav2 Goal**
2. Select the destination on the map.
3. Drag to indicate the desired heading.
4. Release the mouse.

Nav2 will automatically compute a path and navigate the robot to the selected goal.

---

# Complete Workflow

```text
Build Workspace
       │
       ▼
Source Workspace
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
Run start.sh
       │
       ▼
Open RViz
       │
       ▼
Use 2D Pose Estimate
       │
       ▼
Send Nav2 Goal
       │
       ▼
Robot Navigates Autonomously
```

---

# Utility Scripts

## mapping.sh

Launches the mapping workflow.

Supported mapping methods:

* SLAM Toolbox
* Cartographer
* RTAB-Map

---

## start.sh

Starts the navigation stack using the saved map.

---

## verify.sh

Verifies that the required packages and dependencies are correctly installed.

---

## kill.sh

Terminates all running ROS 2, Gazebo, and related processes.

---

# Maps

Generated maps are stored in:

```text
mybot_slam/maps/
```

Example:

```text
maps/

hospital.yaml
hospital.pgm

office.yaml
office.pgm

warehouse.yaml
warehouse.pgm
```

---

# Logs

Log files are stored in:

```text
logs/
```

Example:

```text
logs/

log1/
    gazebo.log
    navigation.log

log2/
    gazebo.log
    navigation.log
```

---

# Tips

* Build the workspace before launching any scripts.
* Source the workspace after every new terminal session.
* Complete mapping before attempting navigation.
* Always save the generated map after mapping.
* Always use **2D Pose Estimate** before sending navigation goals.
* Wait until Nav2 is fully initialized before sending a goal.
* If localization drifts, reset the robot's position using **2D Pose Estimate**.

---

# License

This project is intended for educational, research, and autonomous mobile robot development using ROS 2.
