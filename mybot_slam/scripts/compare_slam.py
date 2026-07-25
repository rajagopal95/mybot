#!/usr/bin/env python3
import os
import sys
import time
import math
import csv
import threading
import numpy as np
import psutil

import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from nav_msgs.msg import OccupancyGrid
from tf2_ros import Buffer, TransformListener, TransformException
import matplotlib.pyplot as plt

class MultiSLAMComparer(Node):
    def __init__(self):
        super().__init__('multi_slam_comparer_node')
        
        self.get_logger().info("==========================================================")
        self.get_logger().info(" Initializing Multi-SLAM Comparer (Toolbox vs Carto vs RTAB) ")
        self.get_logger().info("==========================================================")

        # Storage for maps
        self.map_slam = None
        self.map_carto = None
        self.map_rtab = None

        # Trajectories (x, y)
        self.times = []
        self.traj_slam = []
        self.traj_carto = []
        self.traj_rtab = []
        self.traj_odom = []
        
        self.drift_slam_carto = []
        self.drift_slam_rtab = []
        
        self.mapped_area_slam = []
        self.mapped_area_carto = []
        self.mapped_area_rtab = []
        
        self.cpu_slam = []
        self.cpu_carto = []
        self.cpu_rtab = []
        self.ram_slam = []
        self.ram_carto = []
        self.ram_rtab = []

        self.start_time = time.time()

        # TF listener
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Map Subscriptions
        self.sub_map_slam = self.create_subscription(
            OccupancyGrid,
            '/map_slam_toolbox',
            self.cb_map_slam,
            10
        )
        self.sub_map_carto = self.create_subscription(
            OccupancyGrid,
            '/map_cartographer',
            self.cb_map_carto,
            10
        )
        self.sub_map_rtab = self.create_subscription(
            OccupancyGrid,
            '/map_rtabmap',
            self.cb_map_rtab,
            10
        )

        # Process monitors
        self.proc_slam = None
        self.proc_carto = None
        self.proc_rtab = None
        self.find_slam_processes()

        # Output paths
        self.csv_path = os.path.expanduser('~/mybot_ws/slam_comparison_results.csv')
        self.png_path = os.path.expanduser('~/mybot_ws/slam_comparison_summary.png')

        # CSV initialization
        with open(self.csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Timestamp_sec',
                'SLAM_Toolbox_X', 'SLAM_Toolbox_Y',
                'Cartographer_X', 'Cartographer_Y',
                'RTABMap_X', 'RTABMap_Y',
                'Odom_X', 'Odom_Y',
                'Drift_SLAM_Carto_m', 'Drift_SLAM_RTAB_m',
                'Area_SLAM_m2', 'Area_Carto_m2', 'Area_RTAB_m2',
                'CPU_SLAM_pct', 'CPU_Carto_pct', 'CPU_RTAB_pct',
                'RAM_SLAM_MB', 'RAM_Carto_MB', 'RAM_RTAB_MB'
            ])

        # Timers
        self.create_timer(0.5, self.sample_poses_and_metrics)

        # Thread for Matplotlib Live GUI
        self.plot_running = True
        self.plot_thread = threading.Thread(target=self.live_plot_loop, daemon=True)
        self.plot_thread.start()

    def find_slam_processes(self):
        """Locate PIDs for SLAM Toolbox, Cartographer, and RTAB-Map."""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmd = proc.info.get('cmdline')
                if cmd:
                    cmd_str = ' '.join(cmd)
                    if 'async_slam_toolbox_node' in cmd_str:
                        self.proc_slam = proc
                    elif 'cartographer_node' in cmd_str:
                        self.proc_carto = proc
                    elif 'rtabmap' in cmd_str and 'executable' not in cmd_str:
                        self.proc_rtab = proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    def cb_map_slam(self, msg):
        self.map_slam = msg

    def cb_map_carto(self, msg):
        self.map_carto = msg

    def cb_map_rtab(self, msg):
        self.map_rtab = msg

    def lookup_pose(self, target_frame, source_frame='base_footprint'):
        try:
            now = rclpy.time.Time()
            trans = self.tf_buffer.lookup_transform(
                target_frame,
                source_frame,
                now,
                timeout=Duration(seconds=0.1)
            )
            x = trans.transform.translation.x
            y = trans.transform.translation.y
            return x, y
        except TransformException:
            return None, None

    def calculate_map_area(self, map_msg):
        if map_msg is None:
            return 0.0
        res = map_msg.info.resolution
        data = np.array(map_msg.data)
        known_cells = np.count_nonzero(data >= 0)
        return float(known_cells * (res ** 2))

    def sample_poses_and_metrics(self):
        curr_t = time.time() - self.start_time

        # Poses
        x_slam, y_slam = self.lookup_pose('map_slam_toolbox')
        x_carto, y_carto = self.lookup_pose('map_cartographer')
        x_rtab, y_rtab = self.lookup_pose('map_rtabmap')
        x_odom, y_odom = self.lookup_pose('odom')

        if x_slam is None and x_carto is None and x_rtab is None:
            if self.proc_slam is None or self.proc_carto is None or self.proc_rtab is None:
                self.find_slam_processes()
            return

        # Fallbacks for missing transforms
        if x_slam is None: x_slam, y_slam = x_odom or 0.0, y_odom or 0.0
        if x_carto is None: x_carto, y_carto = x_slam, y_slam
        if x_rtab is None: x_rtab, y_rtab = x_slam, y_slam

        drift_sc = math.hypot(x_slam - x_carto, y_slam - y_carto)
        drift_sr = math.hypot(x_slam - x_rtab, y_slam - y_rtab)

        # Map Areas
        area_slam = self.calculate_map_area(self.map_slam)
        area_carto = self.calculate_map_area(self.map_carto)
        area_rtab = self.calculate_map_area(self.map_rtab)

        # Hardware usage
        c_slam, r_slam = 0.0, 0.0
        c_carto, r_carto = 0.0, 0.0
        c_rtab, r_rtab = 0.0, 0.0

        if self.proc_slam:
            try:
                c_slam = self.proc_slam.cpu_percent()
                r_slam = self.proc_slam.memory_info().rss / (1024 * 1024)
            except Exception: pass

        if self.proc_carto:
            try:
                c_carto = self.proc_carto.cpu_percent()
                r_carto = self.proc_carto.memory_info().rss / (1024 * 1024)
            except Exception: pass

        if self.proc_rtab:
            try:
                c_rtab = self.proc_rtab.cpu_percent()
                r_rtab = self.proc_rtab.memory_info().rss / (1024 * 1024)
            except Exception: pass

        # Record data
        self.times.append(curr_t)
        self.traj_slam.append((x_slam, y_slam))
        self.traj_carto.append((x_carto, y_carto))
        self.traj_rtab.append((x_rtab, y_rtab))
        self.traj_odom.append((x_odom or x_slam, y_odom or y_slam))

        self.drift_slam_carto.append(drift_sc)
        self.drift_slam_rtab.append(drift_sr)
        self.mapped_area_slam.append(area_slam)
        self.mapped_area_carto.append(area_carto)
        self.mapped_area_rtab.append(area_rtab)

        self.cpu_slam.append(c_slam)
        self.cpu_carto.append(c_carto)
        self.cpu_rtab.append(c_rtab)
        self.ram_slam.append(r_slam)
        self.ram_carto.append(r_carto)
        self.ram_rtab.append(r_rtab)

        # Log to CSV
        with open(self.csv_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                f"{curr_t:.2f}",
                f"{x_slam:.4f}", f"{y_slam:.4f}",
                f"{x_carto:.4f}", f"{y_carto:.4f}",
                f"{x_rtab:.4f}", f"{y_rtab:.4f}",
                f"{x_odom or 0.0:.4f}", f"{y_odom or 0.0:.4f}",
                f"{drift_sc:.4f}", f"{drift_sr:.4f}",
                f"{area_slam:.2f}", f"{area_carto:.2f}", f"{area_rtab:.2f}",
                f"{c_slam:.1f}", f"{c_carto:.1f}", f"{c_rtab:.1f}",
                f"{r_slam:.1f}", f"{r_carto:.1f}", f"{r_rtab:.1f}"
            ])

    def live_plot_loop(self):
        plt.ion()
        fig, axs = plt.subplots(2, 2, figsize=(13, 9))
        fig.canvas.manager.set_window_title("Multi-SLAM Real-Time Comparison (Toolbox vs Cartographer vs RTAB-Map)")

        while self.plot_running and rclpy.ok():
            if len(self.times) < 2:
                time.sleep(0.5)
                continue

            times = np.array(self.times)
            slam_pts = np.array(self.traj_slam)
            carto_pts = np.array(self.traj_carto)
            rtab_pts = np.array(self.traj_rtab)
            odom_pts = np.array(self.traj_odom)

            # Subplot 1: Trajectories
            axs[0, 0].cla()
            axs[0, 0].plot(slam_pts[:, 0], slam_pts[:, 1], 'b-', label='SLAM Toolbox', linewidth=2)
            axs[0, 0].plot(carto_pts[:, 0], carto_pts[:, 1], 'r--', label='Cartographer', linewidth=2)
            axs[0, 0].plot(rtab_pts[:, 0], rtab_pts[:, 1], 'g-.', label='RTAB-Map', linewidth=2)
            axs[0, 0].plot(odom_pts[:, 0], odom_pts[:, 1], 'k:', label='EKF Odom', alpha=0.5)
            axs[0, 0].set_title("Robot Trajectories (XY)", fontsize=11, fontweight='bold')
            axs[0, 0].set_xlabel("X (m)")
            axs[0, 0].set_ylabel("Y (m)")
            axs[0, 0].grid(True)
            axs[0, 0].legend(loc='upper right', fontsize='small')

            # Subplot 2: Pose Discrepancies
            axs[0, 1].cla()
            axs[0, 1].plot(times, self.drift_slam_carto, 'm-', label='Toolbox vs Carto (m)', linewidth=2)
            axs[0, 1].plot(times, self.drift_slam_rtab, 'c--', label='Toolbox vs RTAB (m)', linewidth=2)
            axs[0, 1].set_title("Pose Estimation Discrepancy Over Time", fontsize=11, fontweight='bold')
            axs[0, 1].set_xlabel("Time (s)")
            axs[0, 1].set_ylabel("Distance (m)")
            axs[0, 1].grid(True)
            axs[0, 1].legend(loc='upper left', fontsize='small')

            # Subplot 3: Mapped Area
            axs[1, 0].cla()
            axs[1, 0].plot(times, self.mapped_area_slam, 'b-', label='SLAM Toolbox (m²)', linewidth=2)
            axs[1, 0].plot(times, self.mapped_area_carto, 'r--', label='Cartographer (m²)', linewidth=2)
            axs[1, 0].plot(times, self.mapped_area_rtab, 'g-.', label='RTAB-Map (m²)', linewidth=2)
            axs[1, 0].set_title("Environment Mapped Area (m²)", fontsize=11, fontweight='bold')
            axs[1, 0].set_xlabel("Time (s)")
            axs[1, 0].set_ylabel("Area (m²)")
            axs[1, 0].grid(True)
            axs[1, 0].legend(loc='upper left', fontsize='small')

            # Subplot 4: RAM Consumption
            axs[1, 1].cla()
            axs[1, 1].plot(times, self.ram_slam, 'b-', label='SLAM Toolbox (MB)', linewidth=2)
            axs[1, 1].plot(times, self.ram_carto, 'r--', label='Cartographer (MB)', linewidth=2)
            axs[1, 1].plot(times, self.ram_rtab, 'g-.', label='RTAB-Map (MB)', linewidth=2)
            axs[1, 1].set_title("Memory Consumption (RAM MB)", fontsize=11, fontweight='bold')
            axs[1, 1].set_xlabel("Time (s)")
            axs[1, 1].set_ylabel("RAM (MB)")
            axs[1, 1].grid(True)
            axs[1, 1].legend(loc='upper left', fontsize='small')

            plt.tight_layout()
            plt.pause(0.5)

        try:
            plt.savefig(self.png_path, dpi=300)
            self.get_logger().info(f"Saved multi-SLAM summary plot to: {self.png_path}")
        except Exception as e:
            self.get_logger().error(f"Failed to save plot: {e}")

    def generate_final_report(self):
        if not self.times:
            return

        print("\n=======================================================")
        print("        MULTI-SLAM COMPARISON FINAL REPORT METRICS     ")
        print("=======================================================")
        print(f" Total Monitored Duration: {self.times[-1]:.2f} seconds")
        print("-------------------------------------------------------")
        print(" 1. MAPPED AREA COVERAGE:")
        print(f"    - SLAM Toolbox Final Area: {self.mapped_area_slam[-1] if self.mapped_area_slam else 0:.2f} m²")
        print(f"    - Cartographer Final Area: {self.mapped_area_carto[-1] if self.mapped_area_carto else 0:.2f} m²")
        print(f"    - RTAB-Map Final Area:     {self.mapped_area_rtab[-1] if self.mapped_area_rtab else 0:.2f} m²")
        print("-------------------------------------------------------")
        print(" 2. AVERAGE MEMORY CONSUMPTION:")
        print(f"    - SLAM Toolbox Avg RAM:   {np.mean(self.ram_slam) if self.ram_slam else 0:.1f} MB")
        print(f"    - Cartographer Avg RAM:   {np.mean(self.ram_carto) if self.ram_carto else 0:.1f} MB")
        print(f"    - RTAB-Map Avg RAM:       {np.mean(self.ram_rtab) if self.ram_rtab else 0:.1f} MB")
        print("-------------------------------------------------------")
        print(f" Data log saved to:  {self.csv_path}")
        print(f" Summary chart to:   {self.png_path}")
        print("=======================================================\n")

def main(args=None):
    rclpy.init(args=args)
    node = MultiSLAMComparer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.plot_running = False
        node.generate_final_report()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
