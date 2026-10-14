FROM osrf/ros:humble-desktop-full-jammy

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# ROS packages required by mybot (Nav2, SLAM, Gazebo Classic, ros2_control).
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-colcon-common-extensions \
    python3-rosdep \
    ros-humble-slam-toolbox \
    ros-humble-cartographer \
    ros-humble-cartographer-ros \
    ros-humble-navigation2 \
    ros-humble-nav2-bringup \
    ros-humble-robot-localization \
    ros-humble-teleop-twist-keyboard \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-gazebo-plugins \
    ros-humble-gazebo-ros2-control \
    ros-humble-ros2-control \
    ros-humble-ros2-controllers \
    ros-humble-diff-drive-controller \
    ros-humble-joint-state-broadcaster \
    ros-humble-controller-manager \
    ros-humble-laser-filters \
    ros-humble-xacro \
    && rm -rf /var/lib/apt/lists/*

# Cloud Agent runs as ubuntu; the ROS image defaults to root.
RUN if ! id ubuntu >/dev/null 2>&1; then \
      useradd -m -s /bin/bash ubuntu \
      && usermod -aG sudo ubuntu \
      && echo 'ubuntu ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers; \
    fi

USER ubuntu
WORKDIR /home/ubuntu
