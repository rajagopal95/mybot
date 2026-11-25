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

# Native C++ nodes: rclpy cannot deserialize Gazebo Range messages that carry
# FLT_MAX (Python bindings reject it). C++ accepts them and we rewrite to +Inf.
add_executable(ultrasonic_guard src/ultrasonic_guard.cpp)
ament_target_dependencies(ultrasonic_guard rclcpp geometry_msgs sensor_msgs)

add_executable(ultrasonic_range_fixer src/ultrasonic_range_fixer.cpp)
ament_target_dependencies(ultrasonic_range_fixer rclcpp sensor_msgs)

install(TARGETS ultrasonic_guard ultrasonic_range_fixer
  DESTINATION lib/${PROJECT_NAME})

install(DIRECTORY launch worlds config models
  DESTINATION share/${PROJECT_NAME})

ament_package()
