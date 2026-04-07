cmake_minimum_required(VERSION 3.0.2)
project(riobridge)

find_package(catkin REQUIRED COMPONENTS
  roscpp
  rospy
  std_msgs
)

catkin_package(
)

include_directories(
  ${catkin_INCLUDE_DIRS}
)

add_executable(rosbridge src/rosbridge.cpp)
target_link_libraries(rosbridge ${catkin_LIBRARIES})
