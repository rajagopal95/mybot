// Gazebo's ray->Range conversion sets range=FLT_MAX when nothing is hit.
// sensor_msgs/Range (and nav2 RangeSensorLayer) expect +Inf for "no object",
// and RangeSensorLayer silently drops any range > max_range. That left the
// local costmap permanently non-current, so FollowPath never published cmd_vel.
//
// This node remaps:  /<sensor>_raw  ->  /<sensor>  with FLT_MAX/+huge -> +Inf.

#include <cmath>
#include <limits>
#include <string>
#include <vector>

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/range.hpp"

class UltrasonicRangeFixer : public rclcpp::Node
{
public:
  UltrasonicRangeFixer()
  : Node("ultrasonic_range_fixer")
  {
    const std::vector<std::string> sensors{
      "ultrasonic_front_left", "ultrasonic_front_right",
      "ultrasonic_rear_left", "ultrasonic_rear_right",
      "ultrasonic_side_left", "ultrasonic_side_right"};

    for (const auto & sensor : sensors) {
      auto publisher = create_publisher<sensor_msgs::msg::Range>("/" + sensor, rclcpp::SensorDataQoS());
      publishers_.push_back(publisher);

      subscriptions_.push_back(
        create_subscription<sensor_msgs::msg::Range>(
          "/" + sensor + "_raw", rclcpp::SensorDataQoS(),
          [publisher](const sensor_msgs::msg::Range::SharedPtr message) {
            auto out = *message;
            if (!std::isnan(out.range) &&
              (std::isinf(out.range) || out.range >= out.max_range ||
              out.range >= 1.0e38f))
            {
              out.range = std::numeric_limits<float>::infinity();
            }
            if (out.radiation_type > 1) {
              out.radiation_type = sensor_msgs::msg::Range::ULTRASOUND;
            }
            publisher->publish(out);
          }));
    }

    RCLCPP_INFO(get_logger(), "fixing ultrasonic *_raw -> * (FLT_MAX -> +Inf)");
  }

private:
  std::vector<rclcpp::Subscription<sensor_msgs::msg::Range>::SharedPtr> subscriptions_;
  std::vector<rclcpp::Publisher<sensor_msgs::msg::Range>::SharedPtr> publishers_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<UltrasonicRangeFixer>());
  rclcpp::shutdown();
  return 0;
}
