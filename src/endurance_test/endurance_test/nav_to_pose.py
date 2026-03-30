#!/usr/bin/env python3
# Copyright 2022 Clearpath Robotics, Inc.
# Licensed under the Apache License, Version 2.0
# Modified by Pihu, 2026

import rclpy
from turtlebot4_navigation.turtlebot4_navigator import TurtleBot4Directions, TurtleBot4Navigator
from rclpy.node import Node
from std_msgs.msg import String

def main():
    print("HELLO FROM NAV NODE")
    rclpy.init()
    node = NavNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass    
    
    node.destroy_node()

    # Same as goal pose for now
    #waypoint2 = navigator.getPoseStamped([-8.23, 0.309], TurtleBot4Directions.SOUTH_WEST)

    # Set goal pose 
    # goal_pose = navigator.getPoseStamped([-8.23, 0.309], TurtleBot4Directions.SOUTH_WEST)

 

    rclpy.shutdown()
    
class NavNode(Node):
    def __init__(self):
        super().__init__('nav_node')
        
        # setup navigator
        self.navigator = TurtleBot4Navigator()
        
        self.current_command = None
        
        # Subscribe to battery commands
        self.create_subscription(
            String,
            '/battery_command',
            self.command_callback,
            10
        )
        
        self.setup_navigation()
        
    def setup_navigation(self):
        nav = self.navigator
        
        if not nav.getDockedStatus():
            nav.info('Docking before initializing pose')
            nav.dock()
            
        self.initial_pose = nav.getPoseStamped(
            [-2.228, -3.413],
            TurtleBot4Directions.NORTH
        )
        nav.setInitialPose(self.initial_pose)
        
        nav.waitUntilNav2Active()
        
        self.waypoint1 = nav.getPoseStamped(
            [-0.546, -0.0759],
            TurtleBot4Directions.SOUTH_EAST
        )
        
        nav.undock()
        
        self.create_timer(1.0, self.run_mission)
        
    def run_mission(self):
        nav = self.navigator
        
        if self.current_command == 'dock':
            self.get_logger().info('Dock command received')
            nav.startToPose(self.initial_pose)
            nav.dock()
            self.current_command = None
        
        elif self.current_command == 'resume':
            self.get_logger().info('Resume command received')
            nav.undock()
            self.current_command = None
        
        else:
            # Normal navigation loop
            nav.info('Going to waypoint...')
            nav.startToPose(self.waypoint1)
        
            nav.info('Returning')
            nav.startToPose(self.initial_pose)
                
    def command_callback(self, msg):
        self.get_logger().info(f'Received command: {msg.data}')
        self.current_command = msg.data                                                  

if __name__ == '__main__':
    main()
