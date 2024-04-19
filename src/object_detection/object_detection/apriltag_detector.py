import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from cv_bridge import CvBridge
import struct
from apriltag import apriltag, Detector

# Functions for quaternion and rotation matrix conversion
# Code adapted from: https://github.com/rpiRobotics/rpi_general_robotics_toolbox_py
def hat(k):
    """ Returns a 3x3 cross product matrix for a 3x1 vector. """
    khat = np.zeros((3, 3))
    khat[0, 1] = -k[2]
    khat[0, 2] = k[1]
    khat[1, 0] = k[2]
    khat[1, 2] = -k[0]
    khat[2, 0] = -k[1]
    khat[2, 1] = k[0]
    return khat

def q2R(q):
    """ Converts a quaternion into a 3x3 rotation matrix. """
    I = np.identity(3)
    qhat = hat(q[1:4])
    qhat2 = qhat.dot(qhat)
    return I + 2 * q[0] * qhat + 2 * qhat2

class ColorObjDetectionNode(Node):
    def __init__(self):
        super().__init__('color_obj_detection_node')
        self.get_logger().info('Color Object Detection Node Started')
        
        # Initialize AprilTag detector
        self.april_detector = Detector(searchpath=apriltag._get_dll_path(),
                                       families='tagStandard41h12',
                                       nthreads=4,
                                       quad_decimate=1.0,
                                       quad_sigma=0.0,
                                       refine_edges=True,
                                       decode_sharpening=0.25,
                                       debug=False)

        # Tag ID to name mapping
        self.tag_id_to_name = {
            0: "Robbie",
            1: "Tag_One",
            2: "Tag_Two",
            3: "Tag_Three",
            4: "Tag_Four",
            5: "Tag_Five",
            6: "Tag_Six",
            7: "Tag_Seven"
        }
        
        # Declare parameters for color detection
        self.declare_parameter('color_low', [110, 50, 150])
        self.declare_parameter('color_high', [130, 255, 255])
        self.declare_parameter('object_size_min', 1000)

        # Conversion between ROS and OpenCV images
        self.br = CvBridge()

        # Transform listener
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Publishers
        self.pub_detected_obj = self.create_publisher(Image, '/detected_color_object', 10)
        self.pub_detected_obj_pose = self.create_publisher(PoseStamped, '/detected_color_object_pose', 10)

        # Subscribers
        self.sub_rgb = self.create_subscription(Image, '/camera/color/image_raw', self.camera_callback, 10)
        self.sub_depth = self.create_subscription(PointCloud2, '/camera/depth/points', self.camera_callback, 10)

    def camera_callback(self, rgb_msg, points_msg):
        param_color_low = self.get_parameter('color_low').get_parameter_value().integer_array_value
        param_color_high = self.get_parameter('color_high').get_parameter_value().integer_array_value
        param_object_size_min = self.get_parameter('object_size_min').get_parameter_value().integer_value
        
        rgb_image = self.br.imgmsg_to_cv2(rgb_msg, "bgr8")
        gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2GRAY)
        tags = self.april_detector.detect(gray_image)

        for tag in tags:
            tag_name = self.tag_id_to_name.get(tag.tag_id, "Unknown Tag")
            self.get_logger().info(f"Detected {tag_name} with ID {tag.tag_id}")
            print(f"Detected AprilTag with ID: {tag.tag_id}")  # Print the ID of detected AprilTag
            cv2.polylines(rgb_image, [np.array(tag.corners).astype(int)], isClosed=True, color=(0, 255, 0), thickness=2)
            tag_center = np.array(tag.center).astype(int)
            cv2.circle(rgb_image, tuple(tag_center), 5, (0, 255, 0), thickness=-1)

        hsv_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2HSV)
        color_mask = cv2.inRange(hsv_image, param_color_low, param_color_high)
        contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            if w * h < param_object_size_min:
                return  # Object too small, ignore
            center_x = int(x + w / 2)
            center_y = int(y + h / 2)
            self.get_logger().info(f"Object detected at ({center_x}, {center_y})")

def main(args=None):
    rclpy.init(args=args)
    color_obj_detection_node = ColorObjDetectionNode()
    rclpy.spin(color_obj_detection_node)
    color_obj_detection_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
