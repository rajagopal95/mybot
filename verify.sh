echo "Run in this exact order and paste ALL output:"
echo ""
echo "--- 1) confirm amcl node is running and active ---"
echo "ros2 lifecycle get /amcl"
echo ""
echo "--- 2) publish initial pose (again, watch for errors this time) ---"
echo "ros2 topic pub -1 /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \"{header: {frame_id: 'map'}, pose: {pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}\""
echo ""
echo "--- 3) IMMEDIATELY after, check amcl_pose ---"
echo "ros2 topic echo /amcl_pose --once"
echo ""
echo "--- 4) check tf directly for map frame (faster than full view_frames) ---"
echo "ros2 run tf2_ros tf2_echo map odom"
echo "(let it run 3-4 seconds then Ctrl+C, paste what it prints)"
Output

Run in this exact order and paste ALL output:

--- 1) confirm amcl node is running and active ---
ros2 lifecycle get /amcl

--- 2) publish initial pose (again, watch for errors this time) ---
ros2 topic pub -1 /initialpose geometry_msgs/msg/PoseWithCovarianceStamped "{header: {frame_id: 'map'}, pose: {pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"

--- 3) IMMEDIATELY after, check amcl_pose ---
ros2 topic echo /amcl_pose --once

--- 4) check tf directly for map frame (faster than full view_frames) ---
ros2 run tf2_ros tf2_echo map odom
(let it run 3-4 seconds then Ctrl+C, paste what it prints)
