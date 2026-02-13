cmake_minimum_required(VERSION 3.5)
project(rover_description)


find_package(ament_cmake REQUIRED)
find_package(urdf REQUIRED)

# Install resource folders
install(
  DIRECTORY launch meshes models rviz urdf worlds
  DESTINATION share/${PROJECT_NAME}
)

# Environment hook
ament_environment_hooks(
  "${CMAKE_CURRENT_SOURCE_DIR}/env-hooks/rover_description.dsv"
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
