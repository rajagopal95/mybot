#!/usr/bin/env python3
"""
save_map.py

Prompts the user for a map name and saves the currently running
SLAM map (from slam_toolbox / nav2 map_server) into:
    /home/raja/mybot_ws/src/mybot_slam/maps/<map_name>.yaml / .pgm

Usage:
    python3 save_map.py
    (or run directly with `ros2 run` if you wire it up as an entry point)

Requirements:
    - slam.launch.py must already be running (map topic active)
    - nav2_map_server package installed (provides map_saver_cli)
"""

import os
import subprocess
import sys

MAPS_DIR = "/home/raja/mybot_ws/src/mybot/mybot_slam/maps"


def get_map_name() -> str:
    while True:
        name = input("Enter a name for the map (no spaces/extension): ").strip()

        if not name:
            print("Map name cannot be empty. Try again.")
            continue

        if any(c in name for c in " /\\"):
            print("Map name must not contain spaces or slashes. Try again.")
            continue

        yaml_path = os.path.join(MAPS_DIR, f"{name}.yaml")
        if os.path.exists(yaml_path):
            overwrite = input(
                f"'{name}.yaml' already exists in {MAPS_DIR}. Overwrite? [y/N]: "
            ).strip().lower()
            if overwrite != "y":
                continue

        return name


def save_map(map_name: str) -> bool:
    os.makedirs(MAPS_DIR, exist_ok=True)
    output_path = os.path.join(MAPS_DIR, map_name)

    print(f"\nSaving map as: {output_path}.yaml / {output_path}.pgm ...")

    try:
        result = subprocess.run(
            ["ros2", "run", "nav2_map_server", "map_saver_cli", "-f", output_path],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return True

    except subprocess.CalledProcessError as e:
        print("Failed to save map.")
        print(e.stdout)
        print(e.stderr)
        return False

    except subprocess.TimeoutExpired:
        print("Timed out waiting for map_saver_cli. Is SLAM/map topic running?")
        return False

    except FileNotFoundError:
        print("Could not find 'ros2' or 'map_saver_cli'. "
              "Make sure your ROS 2 environment is sourced.")
        return False


def main():
    print("=== Save SLAM Map ===")
    print(f"Target folder: {MAPS_DIR}\n")

    map_name = get_map_name()
    success = save_map(map_name)

    if success:
        print(f"\nMap saved successfully: {map_name}.yaml / {map_name}.pgm")
        sys.exit(0)
    else:
        print("\nMap save failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
