#!/usr/bin/env python3
"""Build a Gazebo/ros2_control-ready fork_robot.urdf.xacro from the raw Fusion export.

    python3 make_fork_robot.py fork_redesigned.urdf.xacro fork_robot.urdf.xacro

The raw export is never edited. Re-run this after every re-export. Joint and link
names are kept exactly as exported (Rigid_17, Rigid_18, Slider_43, ...).

What it does (all of it taken from the old hand-cleaned fork_redesigned_urdf.xacro):
  * adds base_footprint (x forward, on the ground, midway between the drive wheels)
  * drops every mesh collision, adds primitives: body box, wheel cylinders,
    caster spheres, fork tine boxes
  * wheel joints: damping + effort/velocity limits
  * lift joint (prismatic): +Z axis, 0..0.8 m, damping/friction, joint frame moved to the
    carriage centre of mass (ODE does not like a 2 m lever arm on a 64 g link)
  * adds a 200 kg battery ballast link, laser_link / imu_link frames, ros2_control,
    gazebo_ros2_control plugin (with /cmd_vel and /odom remaps), friction, lidar, IMU
"""
import math
import sys
import xml.etree.ElementTree as ET

# ------------------------------------------------------------------ tunables
WHEEL_R = 0.053            # collision radius used for odometry (yaml wheel_radius must match)
WHEEL_W = 0.04
TINE_W = 0.04
# Body collision box in base_link (CAD) frame: panel centres +-3 mm, z 0..0.68
# (top stays below the lidar plane so the lidar never sees the body).
BODY_CENTER = (-0.208, 0.6075, 0.34)
BODY_SIZE = (0.60, 0.325, 0.68)
BALLAST_MASS = 200.0       # set 0 to skip the battery ballast
BALLAST_SIZE = (0.30, 0.25, 0.12)   # forward, left, up
BALLAST_Z = 0.183          # above ground
LIFT_LOWER, LIFT_UPPER = 0.0, 0.8

LEFT_WHEEL, RIGHT_WHEEL = "left_wheel_link_1", "right_wheel_link_1"
CASTERS = ("left_caster_link_1", "right_caster_link_1")
TINES = ("fork_left_link_1", "fork_right_link_1")
LIDAR, IMU = "lidar_link_1", "imu_link_1"
# ---------------------------------------------------------------------------


def fl(s):
    return [float(v) for v in s.split()]


def fmt(v):
    return " ".join(f"{x:.6g}" for x in v)


def main(src, dst):
    root = ET.parse(src).getroot()
    links = {l.get("name"): l for l in root.findall("link")}
    joints = {j.get("name"): j for j in root.findall("joint")}
    by_child = {j.find("child").get("link"): j for j in joints.values()}
    for j in joints.values():
        assert all(abs(v) < 1e-9 for v in fl(j.find("origin").get("rpy"))), \
            f"joint {j.get('name')} has a rotation; script assumes rpy=0 everywhere"

    def world(name):  # position in base_link frame (all joint rpy are zero)
        p = [0.0, 0.0, 0.0]
        while name in by_child:
            j = by_child[name]
            o = fl(j.find("origin").get("xyz"))
            p = [a + b for a, b in zip(p, o)]
            name = j.find("parent").get("link")
        return p

    def com(name):
        i = links[name].find("inertial")
        return fl(i.find("origin").get("xyz")), float(i.find("mass").get("value")), i.find("inertia")

    base = next(n for n in links if n not in by_child)
    lw, rw = world(LEFT_WHEEL), world(RIGHT_WHEEL)
    cas_y = sum(world(c)[1] for c in CASTERS) / len(CASTERS)
    mid = [(lw[0] + rw[0]) / 2, (lw[1] + rw[1]) / 2, lw[2]]
    # forward = away from the casters
    fwd = -1.0 if cas_y > mid[1] else 1.0
    yaw = -fwd * math.pi / 2    # +90 deg when forward is -Y
    # footprint origin (ground, between wheels) in base frame, then base origin in footprint frame
    pb = (mid[0], mid[1], mid[2] - WHEEL_R)
    c, s = math.cos(yaw), math.sin(yaw)
    rot = lambda p: (c * p[0] - s * p[1], s * p[0] + c * p[1], p[2])
    t = tuple(-v for v in rot(pb))
    to_fp = lambda p: tuple(a + b for a, b in zip(rot(p), t))
    left_in_fp = to_fp(lw)[1]
    print(f"forward is {'-Y' if fwd < 0 else '+Y'} of {base}; base_footprint yaw={yaw:.4f} xyz={fmt(t)}")
    print(f"left wheel at y={left_in_fp:+.3f} in footprint (must be positive); track={abs(lw[0]-rw[0]):.4f}")
    lj, rj = by_child[LEFT_WHEEL].get("name"), by_child[RIGHT_WHEEL].get("name")
    print(f"left_wheel_names: [{lj}]  right_wheel_names: [{rj}]")

    # ------------------------------------------------ strip mesh collisions
    for l in links.values():
        for col in l.findall("collision"):
            l.remove(col)

    def add_col(link, xyz, rpy, geom):
        col = ET.Element("collision")
        ET.SubElement(col, "origin", xyz=fmt(xyz), rpy=fmt(rpy))
        g = ET.SubElement(col, "geometry")
        ET.SubElement(g, geom[0], **geom[1])
        l = links[link]
        l.insert(list(l).index(l.find("visual")) + 1, col)

    add_col(base, BODY_CENTER, (0, 0, 0), ("box", {"size": fmt(BODY_SIZE)}))
    for w in (LEFT_WHEEL, RIGHT_WHEEL):
        o, _, _ = com(w)
        add_col(w, o, (0, math.pi / 2, 0),
                ("cylinder", {"radius": f"{WHEEL_R}", "length": f"{WHEEL_W}"}))
    for cn in CASTERS:
        o, _, _ = com(cn)
        zc = (mid[2] - world(cn)[2])    # sphere bottom touches the ground
        add_col(cn, (o[0], o[1], zc), (0, 0, 0), ("sphere", {"radius": f"{WHEEL_R}"}))
    for tn in TINES:
        o, m, inertia = com(tn)
        ii = [float(inertia.get(k)) for k in ("ixx", "iyy", "izz")]
        long_axis = ii.index(min(ii))
        perp = max(ii)
        length = math.sqrt(max(12 * perp / m - TINE_W ** 2, 1e-4))
        size = [TINE_W] * 3
        size[long_axis] = round(length, 3)
        print(f"{tn}: long axis {'xyz'[long_axis]}, length {size[long_axis]} m")
        add_col(tn, o, (0, 0, 0), ("box", {"size": fmt(size)}))

    # ------------------------------------------------ wheel joints
    for jn in (lj, rj):
        j = joints[jn]
        ET.SubElement(j, "dynamics", damping="0.2", friction="0.0")
        ET.SubElement(j, "limit", effort="300", velocity="20")

    # ------------------------------------------------ lift joint
    lift = next(j for j in joints.values() if j.get("type") == "prismatic")
    holder = lift.find("child").get("link")
    d, _, _ = com(holder)
    o = fl(lift.find("origin").get("xyz"))
    lift.find("origin").set("xyz", fmt([a + b for a, b in zip(o, d)]))
    for j in joints.values():
        if j.find("parent").get("link") == holder:
            oo = fl(j.find("origin").get("xyz"))
            j.find("origin").set("xyz", fmt([a - b for a, b in zip(oo, d)]))
    for tag in ("inertial", "visual"):
        e = links[holder].find(tag + "/origin")
        e.set("xyz", fmt([a - b for a, b in zip(fl(e.get("xyz")), d)]))
    lift.find("axis").set("xyz", "0 0 1")
    lim = lift.find("limit")
    lim.attrib.clear()
    lim.set("lower", f"{LIFT_LOWER}")
    lim.set("upper", f"{LIFT_UPPER}")
    lim.set("effort", "500")
    lim.set("velocity", "0.2")
    ET.SubElement(lift, "dynamics", damping="200", friction="50")
    lift_name = lift.get("name")
    print(f"lift joint {lift_name}: axis +Z, {LIFT_LOWER}..{LIFT_UPPER} m, frame moved to carriage COM")

    # ------------------------------------------------ header / new elements
    root.set("name", "fork_robot")
    root.set("xmlns:xacro", "http://www.ros.org/wiki/xacro")
    root.insert(0, ET.Element("xacro:arg", name="use_camera", default="false"))

    ballast_xy = to_fp(BODY_CENTER)
    ixx = BALLAST_MASS / 12 * (BALLAST_SIZE[1] ** 2 + BALLAST_SIZE[2] ** 2)
    iyy = BALLAST_MASS / 12 * (BALLAST_SIZE[0] ** 2 + BALLAST_SIZE[2] ** 2)
    izz = BALLAST_MASS / 12 * (BALLAST_SIZE[0] ** 2 + BALLAST_SIZE[1] ** 2)
    lo, _, _ = com(LIDAR)
    ballast = ""
    if BALLAST_MASS > 0:
        ballast = f"""
  <!-- Battery ballast, centred in the body and low. The CAD parts alone put the CoM about
       0.41 m high; this pulls it to about 0.25 m and adds wheel traction. -->
  <link name="battery_link">
    <inertial>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <mass value="{BALLAST_MASS}"/>
      <inertia ixx="{ixx:.4f}" ixy="0" ixz="0" iyy="{iyy:.4f}" iyz="0" izz="{izz:.4f}"/>
    </inertial>
  </link>
  <joint name="battery_joint" type="fixed">
    <parent link="base_footprint"/><child link="battery_link"/>
    <origin xyz="{ballast_xy[0]:.4f} {ballast_xy[1]:.4f} {BALLAST_Z}" rpy="0 0 0"/>
  </joint>
"""
    new = f"""<root>
  <!-- x forward, z up, on the ground midway between the drive wheels. Tiny inertia so
       Gazebo does not invent a 1 kg CoM on the floor. -->
  <link name="base_footprint">
    <inertial>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <mass value="0.01"/>
      <inertia ixx="1e-6" ixy="0" ixz="0" iyy="1e-6" iyz="0" izz="1e-6"/>
    </inertial>
  </link>
  <joint name="base_footprint_joint" type="fixed">
    <parent link="base_footprint"/><child link="{base}"/>
    <origin xyz="{fmt(t)}" rpy="0 0 {yaw:.6f}"/>
  </joint>
{ballast}
  <!-- Sensor frames. laser_link +X points at the forks (the back), same as the old model,
       so the 90..270 deg scan window and fork_scan_filter.yaml face the front panel.
       Origin = lidar mesh centre (the exported link origin sits below the lidar). -->
  <link name="laser_link">
    <inertial><mass value="0.001"/><inertia ixx="1e-6" ixy="0" ixz="0" iyy="1e-6" iyz="0" izz="1e-6"/></inertial>
  </link>
  <joint name="laser_joint" type="fixed">
    <parent link="{LIDAR}"/><child link="laser_link"/>
    <origin xyz="{fmt(lo)}" rpy="0 0 {math.pi / 2:.6f}"/>
  </joint>
  <link name="imu_link">
    <inertial><mass value="0.001"/><inertia ixx="1e-6" ixy="0" ixz="0" iyy="1e-6" iyz="0" izz="1e-6"/></inertial>
  </link>
  <joint name="imu_joint" type="fixed">
    <parent link="{IMU}"/><child link="imu_link"/>
    <!-- +X is the front panel, same as base_footprint -->
    <origin xyz="0 0 0" rpy="0 0 {-yaw:.6f}"/>
  </joint>

  <ros2_control name="GazeboSystem" type="system">
    <hardware><plugin>gazebo_ros2_control/GazeboSystem</plugin></hardware>
    <joint name="{lj}">
      <command_interface name="velocity"><param name="min">-10</param><param name="max">10</param></command_interface>
      <state_interface name="position"/><state_interface name="velocity"/>
    </joint>
    <joint name="{rj}">
      <command_interface name="velocity"><param name="min">-10</param><param name="max">10</param></command_interface>
      <state_interface name="position"/><state_interface name="velocity"/>
    </joint>
    <joint name="{lift_name}">
      <command_interface name="position"/>
      <state_interface name="position"><param name="initial_value">0.0</param></state_interface>
      <state_interface name="velocity"/>
    </joint>
  </ros2_control>

  <gazebo>
    <plugin name="gazebo_ros2_control" filename="libgazebo_ros2_control.so">
      <robot_param>robot_description</robot_param>
      <robot_param_node>robot_state_publisher</robot_param_node>
      <parameters>$(find mybot_gazebo)/config/fork_controllers.yaml</parameters>
      <ros>
        <remapping>diff_drive_controller/odom:=/odom</remapping>
        <remapping>diff_drive_controller/cmd_vel_unstamped:=/cmd_vel</remapping>
      </ros>
    </plugin>
  </gazebo>

  <gazebo reference="{base}"><material>Gazebo/Grey</material><self_collide>false</self_collide></gazebo>
  <gazebo reference="{LEFT_WHEEL}">
    <material>Gazebo/Black</material>
    <mu1>1.2</mu1><mu2>1.2</mu2><kp>1000000.0</kp><kd>100.0</kd><minDepth>0.001</minDepth><maxVel>1.0</maxVel>
  </gazebo>
  <gazebo reference="{RIGHT_WHEEL}">
    <material>Gazebo/Black</material>
    <mu1>1.2</mu1><mu2>1.2</mu2><kp>1000000.0</kp><kd>100.0</kd><minDepth>0.001</minDepth><maxVel>1.0</maxVel>
  </gazebo>
  <gazebo reference="{CASTERS[0]}">
    <mu1>0.05</mu1><mu2>0.05</mu2><kp>1000000.0</kp><kd>10.0</kd><minDepth>0.001</minDepth><maxVel>1.0</maxVel>
  </gazebo>
  <gazebo reference="{CASTERS[1]}">
    <mu1>0.05</mu1><mu2>0.05</mu2><kp>1000000.0</kp><kd>10.0</kd><minDepth>0.001</minDepth><maxVel>1.0</maxVel>
  </gazebo>

  <gazebo reference="laser_link">
    <sensor name="lidar_sensor" type="ray">
      <always_on>true</always_on>
      <visualize>true</visualize>
      <update_rate>30</update_rate>
      <ray>
        <scan>
          <horizontal>
            <samples>180</samples>
            <resolution>1</resolution>
            <!-- 90 deg to 270 deg in laser_link: faces the front panel -->
            <min_angle>1.5708</min_angle>
            <max_angle>4.7124</max_angle>
          </horizontal>
        </scan>
        <range><min>0.12</min><max>10.0</max><resolution>0.01</resolution></range>
        <noise><type>gaussian</type><mean>0.0</mean><stddev>0.01</stddev></noise>
      </ray>
      <plugin name="laser_plugin" filename="libgazebo_ros_ray_sensor.so">
        <ros><remapping>~/out:=/scan</remapping></ros>
        <frame_name>laser_link</frame_name>
        <output_type>sensor_msgs/LaserScan</output_type>
      </plugin>
    </sensor>
  </gazebo>

  <gazebo reference="imu_link">
    <sensor name="imu_sensor" type="imu">
      <always_on>true</always_on>
      <update_rate>100</update_rate>
      <visualize>false</visualize>
      <imu>
        <angular_velocity>
          <x><noise type="gaussian"><mean>0.0</mean><stddev>0.0002</stddev></noise></x>
          <y><noise type="gaussian"><mean>0.0</mean><stddev>0.0002</stddev></noise></y>
          <z><noise type="gaussian"><mean>0.0</mean><stddev>0.0002</stddev></noise></z>
        </angular_velocity>
        <linear_acceleration>
          <x><noise type="gaussian"><mean>0.0</mean><stddev>0.017</stddev></noise></x>
          <y><noise type="gaussian"><mean>0.0</mean><stddev>0.017</stddev></noise></y>
          <z><noise type="gaussian"><mean>0.0</mean><stddev>0.017</stddev></noise></z>
        </linear_acceleration>
      </imu>
      <plugin name="imu_plugin" filename="libgazebo_ros_imu_sensor.so">
        <ros><namespace>/</namespace><remapping>~/out:=imu</remapping></ros>
        <frame_name>imu_link</frame_name>
        <initial_orientation_as_reference>false</initial_orientation_as_reference>
      </plugin>
    </sensor>
  </gazebo>
</root>"""
    for e in ET.fromstring(new):
        root.append(e)

    ET.indent(root, space="  ")
    header = ("<?xml version=\"1.0\"?>\n<!-- GENERATED by make_fork_robot.py from the Fusion export; "
              "do not edit, re-run the script. -->\n")
    with open(dst, "w") as f:
        f.write(header + ET.tostring(root, encoding="unicode") + "\n")
    print("wrote", dst)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
