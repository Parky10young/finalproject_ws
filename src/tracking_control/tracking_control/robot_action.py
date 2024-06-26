import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
import numpy as np
import time

from std_msgs.msg import String, Float32MultiArray
from geometry_msgs.msg import PoseStamped


class WaypointPublisher(Node):

    def __init__(self):
        super().__init__('waypoint_publisher')
        self.publisher_ = self.create_publisher(Float32MultiArray, 'waypoint_topic', 10)
        timer_period = 1  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 1
        self.curr_pose = None
        self.akg = None
        self.current_pos_subscriber = self.create_subscription(String, '/nav2_status', self.current_position_callback, 10)
        self.current_pos_subscriber = self.create_subscription(String, '/akg', self.acknowledgement_callback, 10)
        self.object_pose_subscriber = self.create_subscription(PoseStamped, '/detected_color_object_pose', self.object_pose_callback, 10)
        
    def timer_callback(self):
        #loop between waypoint 1 and start position
        #go to waypoint 1
        if self.akg !="ok":
            waypoint = Float32MultiArray()
            waypoint.data = [1.0,1.0,np.pi/2]
            self.publisher_.publish(waypoint)
            self.get_logger().info('Publishing: "%s"' % waypoint.data)
            self.i == 2
            return
            
        #go to start
        elif self.curr_pose == "Arrived" and self.akg == "ok":
            waypoint = Float32MultiArray()
            waypoint.data = [0.0,0.0,0.0]
            self.publisher_.publish(waypoint)
            self.get_logger().info('Publishing: "%s"' % waypoint.data)
            self.i = 3
            time.sleep(1)

            return
        '''
        #change waypoint
        else:
            if  self.i == 2 and self.curr_pose== "Arrived":
                self.i = 0
                return
            elif self.i == 3 and self.curr_pose== "Arrived":
                self.i = 1
                return
            return
            '''
        
    def current_position_callback(self, msg):
        #check if robot has arrived to waypoint
        self.curr_pose = msg.data

    def acknowledgement_callback(self, msg):
        #check if robot has recieved waypoint
        self.akg = msg.data

    def object_pose_callback(self, detected_obj_pose):
        print("coordinate recieved")
        #print object coordinates 
        '''
         detected_obj_pose.pose.position.x = cp_robot[0]
            detected_obj_pose.pose.position.y = cp_robot[1]
            detected_obj_pose.pose.position.z = cp_robot[2]
            '''
        x = detected_obj_pose.pose.position.x
        y = detected_obj_pose.pose.position.y
        z = detected_obj_pose.pose.position.z
        print("Object Position")
        print("X:",x,"y:",y,"z:",z)

def main(args=None):
    rclpy.init(args=args)

    waypoint_publisher = WaypointPublisher()

    rclpy.spin(waypoint_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    waypoint_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
