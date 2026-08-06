cmake_minimum_required(VERSION 3.0)
project(netzsch_tma402f3)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
)

catkin_python_setup()

catkin_package(
  CATKIN_DEPENDS rospy std_msgs
  )

catkin_install_python(
  PROGRAMS
    scripts/tma_control_gui.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

include_directories(
  ${catkin_INCLUDE_DIRS}
)
