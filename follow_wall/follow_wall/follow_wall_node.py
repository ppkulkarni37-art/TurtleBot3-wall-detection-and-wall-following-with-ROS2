import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

class FollowWallNode(Node):
    def __init__(self):
        super().__init__('follow_wall_node')

        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
        self.subscription = self.create_subscription(
            LaserScan,
            'scan',
            self.scan_callback,
            10
        )

    def scan_callback(self, msg):
        twist = Twist()

# 75 degrees front vision
        front_ranges = msg.ranges[0:38] + msg.ranges[322:360]
# 75 degrees right vision
        right_ranges = msg.ranges[232:308]
        # Filter out inf/nan values
        front_ranges = [r for r in front_ranges if r != float('inf') and r == r]
        right_ranges = [r for r in right_ranges if r != float('inf') and r == r]

        front = min(front_ranges) if front_ranges else 999
        right = min(right_ranges) if right_ranges else 999

        SAFE_DIST     = 0.5
        FORWARD_SPEED = 0.3
        TURN_SPEED    = 0.2

        # PHASE 1: All clear → drive forward
        if front > SAFE_DIST and right > SAFE_DIST:
            twist.linear.x  = FORWARD_SPEED
            twist.angular.z = 0.0
            self.get_logger().info(f'PHASE 1: Driving | front: {front:.2f} right: {right:.2f}')

        # PHASE 2: Wall ahead → STOP, turn LEFT in place
        elif front <= SAFE_DIST and right > SAFE_DIST:
            twist.linear.x  = 0.0
            twist.angular.z = TURN_SPEED
            self.get_logger().info(f'PHASE 2: Turning LEFT | front: {front:.2f} right: {right:.2f}')

        # PHASE 3: Right wall found, front clear → follow wall
        elif front > SAFE_DIST and right <= SAFE_DIST:
            twist.linear.x  = FORWARD_SPEED
            twist.angular.z = 0.0
            self.get_logger().info(f'PHASE 3: Following wall | front: {front:.2f} right: {right:.2f}')

        # PHASE 4: Corner → STOP, turn LEFT in place
        elif front <= SAFE_DIST and right <= SAFE_DIST:
            twist.linear.x  = 0.0
            twist.angular.z = TURN_SPEED
            self.get_logger().info(f'PHASE 4: Corner! | front: {front:.2f} right: {right:.2f}')

        self.publisher_.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = FollowWallNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()