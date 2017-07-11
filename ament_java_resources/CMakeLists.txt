cmake_minimum_required(VERSION 3.5)

project(ament_java_resources NONE)

find_package(ament_cmake REQUIRED)

ament_index_register_resource(
    "templates"
    CONTENT_FILE "classpath.sh.template"
    PACKAGE_NAME "ament_build_type_gradle_classpath_sh")

ament_index_register_resource(
    "templates"
    CONTENT_FILE "classpath.bat.template"
    PACKAGE_NAME "ament_build_type_gradle_classpath_bat")

ament_package()
