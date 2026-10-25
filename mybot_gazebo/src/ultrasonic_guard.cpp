#include <algorithm>
#include <cmath>
#include <limits>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/range.hpp"

class UltrasonicGuard : public rclcpp::Node
{
public:
  UltrasonicGuard()
  : Node("ultrasonic_guard")
  {
    declare_parameter<std::string>("input_topic", "/cmd_vel_raw");
    declare_parameter<std::string>("output_topic", "/cmd_vel");
    declare_parameter<double>("front_stop", 0.25);
    declare_parameter<double>("front_slow", 0.60);
    declare_parameter<double>("rear_stop", 0.30);
    declare_parameter<double>("rear_slow", 0.70);
    declare_parameter<double>("side_stop", 0.05);
    declare_parameter<double>("stale_after", 0.5);
    declare_parameter<bool>("stop_on_stale", false);

    const std::vector<std::string> sensors{
      "ultrasonic_front_left", "ultrasonic_front_right",
      "ultrasonic_rear_left", "ultrasonic_rear_right",
      "ultrasonic_side_left", "ultrasonic_side_right"};
    for (const auto & sensor : sensors) {
      range_subscriptions_.push_back(create_subscription<sensor_msgs::msg::Range>(
          "/" + sensor, rclcpp::SensorDataQoS(),
          [this, sensor](const sensor_msgs::msg::Range::SharedPtr message) {
            on_range(sensor, *message);
          }));
    }

    command_publisher_ = create_publisher<geometry_msgs::msg::Twist>(
      get_parameter("output_topic").as_string(), 10);
    command_subscription_ = create_subscription<geometry_msgs::msg::Twist>(
      get_parameter("input_topic").as_string(), 10,
      std::bind(&UltrasonicGuard::on_command, this, std::placeholders::_1));

    RCLCPP_INFO(
      get_logger(), "guarding %s -> %s",
      get_parameter("input_topic").as_string().c_str(),
      get_parameter("output_topic").as_string().c_str());
  }

private:
  struct Reading
  {
    double range;
    rclcpp::Time stamp;
  };

  static constexpr double kInfinity = std::numeric_limits<double>::infinity();

  void on_range(const std::string & sensor, const sensor_msgs::msg::Range & message)
  {
    double range = message.range;
    if (std::isnan(range)) {
      return;
    }
    if (range < message.min_range) {
      range = message.min_range;
    } else if (std::isinf(range) || range >= message.max_range) {
      range = kInfinity;
    }
    readings_[sensor] = {range, now()};
  }

  std::pair<double, bool> group_min(const std::vector<std::string> & sensors) const
  {
    const auto current_time = now();
    double best = kInfinity;
    bool stale = false;
    const double stale_after = get_parameter("stale_after").as_double();
    for (const auto & sensor : sensors) {
      const auto reading = readings_.find(sensor);
      if (reading == readings_.end() || (current_time - reading->second.stamp).seconds() > stale_after) {
        stale = true;
        continue;
      }
      best = std::min(best, reading->second.range);
    }
    return {best, stale};
  }

  static double scale(const double range, const double stop, const double slow)
  {
    if (range <= stop) {
      return 0.0;
    }
    if (range >= slow) {
      return 1.0;
    }
    return (range - stop) / (slow - stop);
  }

  void on_command(const geometry_msgs::msg::Twist::SharedPtr command)
  {
    const std::vector<std::string> front{"ultrasonic_front_left", "ultrasonic_front_right"};
    const std::vector<std::string> rear{"ultrasonic_rear_left", "ultrasonic_rear_right"};
    const std::vector<std::string> sides{"ultrasonic_side_left", "ultrasonic_side_right"};

    double multiplier = 1.0;
    bool lock_angular = false;
    std::string reason;
    const double velocity = command->linear.x;

    if (velocity != 0.0) {
      const bool forward = velocity > 0.0;
      const auto [range, stale] = group_min(forward ? front : rear);
      const std::string prefix = forward ? "front" : "rear";
      multiplier = scale(
        range, get_parameter(prefix + "_stop").as_double(),
        get_parameter(prefix + "_slow").as_double());
      reason = prefix + " range " + std::to_string(range) + " m";
      if (stale && get_parameter("stop_on_stale").as_bool()) {
        multiplier = 0.0;
        reason = prefix + " sensor data stale";
      }

      const auto [side_range, unused_stale] = group_min(sides);
      (void)unused_stale;
      if (side_range <= get_parameter("side_stop").as_double()) {
        lock_angular = true;
        multiplier = std::min(multiplier, 0.3);
        reason = "side range " + std::to_string(side_range) + " m";
      }
    }

    auto output = *command;
    output.linear.x *= multiplier;
    output.angular.z = lock_angular ? 0.0 : command->angular.z * (velocity != 0.0 ? multiplier : 1.0);

    if (multiplier < 1.0 || lock_angular) {
      RCLCPP_WARN_THROTTLE(
        get_logger(), *get_clock(), 2000, "limiting motion (%s), scale=%.2f",
        reason.c_str(), multiplier);
    }
    command_publisher_->publish(output);
  }

  std::unordered_map<std::string, Reading> readings_;
  std::vector<rclcpp::Subscription<sensor_msgs::msg::Range>::SharedPtr> range_subscriptions_;
  rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr command_subscription_;
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr command_publisher_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<UltrasonicGuard>());
  rclcpp::shutdown();
  return 0;
}
