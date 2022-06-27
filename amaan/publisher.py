#!/usr/bin/env python

import rclpy
from rclpy.node import Node
import cv2

from std_msgs.msg import Byte

class VideoCamera(object):
    def __init__(self, scale_percent):
        """
        @param scale_percent: percent of original size that you want to scale to
        """
        self.video = cv2.VideoCapture(0)    # open webcam
        self.scale_percent = scale_percent

    def __del__(self):
        self.video.release()

    def _resizeImage(self, img, percent):
        width = int(img.shape[1] * percent / 100)
        height = int(img.shape[0] * percent / 100)
        dim = (width, height)
        img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

        return img, dim

    def get_frame(self):
        success, image = self.video.read()
        image, _ = self._resizeImage(image, self.scale_percent)
        image = cv2.flip(image, 1)   # flip horizontally
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

class CameraPublisher(Node):
    def __init__(self, camera: VideoCamera, fps: int):
        super().__init__('camera_publisher')
        self._publisher = self.create_publisher(Byte, 'camera_topic', 10)

        # create a timer callback that gets executed every "timer_period" seconds
        self.fps = fps
        timer_period: float = 1 / float(fps)  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0
        self.cam = camera

    def timer_callback(self):
        frame = Byte()
        frame.data = self.cam.get_frame()
        self._publisher.publish(frame)

        self.get_logger().info("Publishing Frame %d" % self.i)
        self.i += 1

def main(args=None):
    rclpy.init(args=args)

    camera_publisher = CameraPublisher()

    rclpy.spin(camera_publisher)

    # Destroy node (optional cuz garbage collector will do this)
    camera_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()