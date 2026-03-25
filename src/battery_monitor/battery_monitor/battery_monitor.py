"""Monitor battery percentage, and issue commands at 20% and 80% threshold"""

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import BatteryState
from std_msgs.msg import String


class BatteryMonitorNode(Node):
    def __init__(self):
        super().__init__('battery_monitor_node')

        self.initial_battery = None
        self.threshold_delta = 0.05 # 5%
        self.current_mode = None

        self.subscription = self.create_subscription(
            BatteryState,
            '/battery_state',
            self.battery_callback,
            10
        )

        self.command_publisher = self.create_publisher(
            String,
            '/battery_command',
            10
        )

        self.get_logger().info('Battery monitor node started.')

    def battery_callback(self, msg: BatteryState):
        percentage = msg.percentage

        if percentage is None or percentage < 0.0:
            self.get_logger().warn('Received invalid battery percentage.')
            return

        self.get_logger().info(f'Battery percentage: {percentage * 100:.1f}%')

        # Store initial battery once
        if self.initial_battery is None:
	    self.initial_battery = percentage
	    self.get_logger().info(f'Initial battery set: {percentage*100:.1f}%')
	    return
	    
        low_threshold = max(0.0, self.initial_battery - self.threshold_delta)
        high_threshold = min(1.0, self.initial_battery + self.threshold_delta)
	
        self.get_logger().info(
          f'Battery: {percentage*100:.1f}% | Low: {low_threshold*100:.1f}% | High: {high_threshold*100:.1f}%'
        )    
	
        if percentage <= low_threshold:
            if self.current_mode != 'dock':
                self.publish_command('dock')
                self.current_mode = 'dock'

        elif percentage >= high_threshold:
            if self.current_mode != 'resume':
                self.publish_command('resume')
                self.current_mode = 'resume'

    def publish_command(self, command: str):
        msg = String()
        msg.data = command
        self.command_publisher.publish(msg)
        self.get_logger().info(f'Published command: {command}')


def main(args=None):
    rclpy.init(args=args)
    node = BatteryMonitorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
