# Forklift OS dashboard

A responsive, multi-page ROS 2 dashboard concept for an autonomous forklift and intelligent pallet handling project.

It is also an installable Progressive Web App (PWA). Serve it over HTTPS or localhost, open `index.html`, then use **Install app** in the top bar or your browser's install option. On iPhone/iPad, open the page in Safari and choose **Share → Add to Home Screen**. The app shell and demo interface are cached for offline use after the first visit; ROS 2 and camera streams require network access.

## Pages

- `index.html` — operations overview
- `map.html` — occupancy map, robot localization, and navigation goal selection
- `robot.html` — power, motion, lift, subsystem health, manual jog, and emergency stop
- `camera.html` — camera stream and pallet detection
- `missions.html` — pick-and-place task sequence and operator actions
- `logs.html` — event log and CSV export
- `settings.html` — rosbridge, video server, map frame, and topic configuration

Use **Demo mode** from the header for a review presentation. The demo selection stays active as you move between pages in the same browser tab. Choose **ROS 2 connection** to edit endpoints and topic names; live mode reconnects as you navigate between pages.

## ROS 2 integration

This browser UI connects through `rosbridge_suite` and expects these defaults (editable on the ROS settings page):

| Topic | Message type | Purpose |
|---|---|---|
| `/map` | `nav_msgs/OccupancyGrid` | SLAM / Nav2 map |
| `/amcl_pose` | `geometry_msgs/PoseWithCovarianceStamped` | Robot pose |
| `/odom` | `nav_msgs/Odometry` | Speed feedback |
| `/battery_state` | `sensor_msgs/BatteryState` | Battery percentage |
| `/fork_height` | `std_msgs/Float32` | Fork height in metres |
| `/mission_status` | `std_msgs/String` | JSON such as `{"step":2,"text":"Align forks","progress":35}` |
| `/pallet_detections` | `std_msgs/String` | JSON detection list with label, confidence, bounding box, and optional image dimensions |
| `/camera/image_raw` | `sensor_msgs/Image` | Camera topic streamed by `web_video_server` |
| `/cmd_vel` | `geometry_msgs/Twist` | Manual drive command |
| `/fork_cmd` | `std_msgs/Float32` | Fork target height in metres |
| `/emergency_stop` | `std_msgs/Bool` | Emergency stop request |
| `/goal_pose` | `geometry_msgs/PoseStamped` | Map navigation goal |

Open `settings.html`, enter the browser-reachable rosbridge WebSocket URL (for example `ws://robot-host:9090`) and video server URL (for example `http://robot-host:8080`), adjust topic names to match your ROS graph, and connect. The browser and robot network must allow these endpoints. The MJPEG stream URL is constructed as `/stream?topic=<camera-topic>&type=mjpeg`.

For local presentation or installation, start a static web server from this folder and open the printed local URL. For example, if Python is installed, run `python -m http.server 8000` in this directory and open `http://localhost:8000/`. For installation on other devices, host the folder on HTTPS and open its URL on each device.

## Adapt before hardware operation

The page structure and data contracts are a project-ready starting point. Update the topic names, ROS message types, fork limits, units, and mission interface to match your robot. In particular, connect mission start/pause/abort to your project's ROS action or service interface and connect the emergency stop to a safety-rated controller. The displayed health and diagnostic examples are illustrative until backed by real ROS diagnostics.
