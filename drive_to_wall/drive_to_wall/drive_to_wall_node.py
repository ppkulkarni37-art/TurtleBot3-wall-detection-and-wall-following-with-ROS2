import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

class DriveToWallNode(Node):
    def __init__(self):
        super().__init__('drive_to_wall_node')
        
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
        self.subscription = self.create_subscription(
            LaserScan,
            'scan',
            self.scan_callback,
            10
        )

    def scan_callback(self, msg):
        twist = Twist()
        
        front_distance = msg.ranges[0]
        self.get_logger().info(f'Front distance: {front_distance:.2f}')
        
        if front_distance > 1.0:
            twist.linear.x = 0.5
            self.get_logger().info('Driving forward...')
        else:
            twist.linear.x = 0.0
            self.get_logger().info('Wall detected! Stopping.')
        
        self.publisher_.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = DriveToWallNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()