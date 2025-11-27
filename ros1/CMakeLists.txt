cmake_minimum_required(VERSION 2.8.0)
project(netzsch_instrument_ros1)

#catkin_python_setup()

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  message_generation
)

add_service_files(
  FILES
  NETZSCH_Measurement.srv
)

generate_messages(
  DEPENDENCIES
  std_msgs
)

catkin_package(
  CATKIN_DEPENDS rospy std_msgs message_runtime
  )


catkin_install_python(
  PROGRAMS
    scripts/netzsch_measurement_server.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

include_directories(
  ${catkin_INCLUDE_DIRS}
)
