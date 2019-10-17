cmake_minimum_required(VERSION 3.5)

project(ament_java_resources NONE)

find_package(ament_cmake REQUIRED)

ament_index_register_resource(
    "templates"
    CONTENT_FILE "classpath.sh.template"
    PACKAGE_NAME "ament_build_type_gradle_classpath_sh")

ament_index_register_resource(
    "templates"
    CONTENT_FILE "classpath.dsv.template"
    PACKAGE_NAME "ament_build_type_gradle_classpath_dsv")

ament_index_register_resource(
    "templates"
    CONTENT_FILE "classpath.bat.template"
    PACKAGE_NAME "ament_build_type_gradle_classpath_bat")

ament_index_register_resource(
    "templates"
    CONTENT_FILE "jni_library_path.sh.template"
    PACKAGE_NAME "ament_build_type_gradle_jni_library_path_sh")

ament_index_register_resource(
    "templates"
    CONTENT_FILE "jni_library_path.bat.template"
    PACKAGE_NAME "ament_build_type_gradle_jni_library_path_bat")

ament_index_register_resource(
    "templates"
    CONTENT_FILE "jni_library_path.dsv.template"
    PACKAGE_NAME "ament_build_type_gradle_jni_library_path_dsv")

ament_package()
