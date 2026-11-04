cmake_minimum_required(VERSION 3.8)
project(mybot_gazebo)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(gazebo_ros REQUIRED)
find_package(gazebo_plugins REQUIRED)
find_package(robot_state_publisher REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

# A native subscriber is required because several Gazebo Range topics cannot
# be deserialized by rclpy in this simulation.  The local costmap already
# proves the native ROS 2 subscription path is valid for those messages.
add_executable(ultrasonic_guard src/ultrasonic_guard.cpp)
ament_target_dependencies(ultrasonic_guard rclcpp geometry_msgs sensor_msgs)

install(TARGETS ultrasonic_guard
  DESTINATION lib/${PROJECT_NAME})

install(DIRECTORY launch worlds config models
  DESTINATION share/${PROJECT_NAME})

ament_package()
