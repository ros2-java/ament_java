# Copyright 2016-2017 Esteve Fernandez <esteve@apache.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Based on
# https://github.com/ament/ament_tools/blob/master/ament_tools/build_types/ament_python.py
# Copyright 2014 Open Source Robotics Foundation, Inc.
"""Implements the BuildType support for gradle based ament packages."""

import os
import shutil
from distutils import dir_util

from ament_package.templates import get_environment_hook_template_path
from ament_build_type_gradle.templates import get_environment_hook_classpath_template_path

from ament_package.templates import configure_string
from ament_package.templates import get_package_level_template_names

from ament_tools.helper import extract_argument_group
from ament_tools.build_type import BuildAction
from ament_tools.build_type import BuildType
from ament_tools.build_types.common import expand_package_level_setup_files
from ament_tools.helper import deploy_file
from ament_tools.verbs.build_pkg import cli
from ament_tools.verbs import VerbExecutionError

IS_WINDOWS = os.name == 'nt'


class AmentGradleBuildType(BuildType):
    build_type = 'ament_gradle'
    description = "ament package built with Gradle"

    def _build_file_tree(self, start_path):
        out_dirnames = set()
        out_filenames = set()
        for dirname, dirnames, filenames in os.walk(start_path):
            for subdirname in dirnames:
                out_dirnames.add(
                    os.path.relpath(
                        os.path.join(dirname, subdirname), start=start_path))

            for filename in filenames:
                out_filenames.add(
                    os.path.relpath(
                        os.path.join(dirname, filename), start=start_path))
        return (out_dirnames, out_filenames)

    def _ament_gradle_recursive_dependencies(self, context):
        for export in context.package_manifest.exports:
            if export.tagname == 'ament_gradle_recursive_dependencies':
                return True
        return False

    def _get_ament_args(self, context):
        cmd_args = [
            '-Pament.source_space=' + context.source_space,
            '-Pament.build_space=' + context.build_space,
            '-Pament.install_space=' + context.install_space,
            '-Pament.dependencies=' + ':'.join(context.build_dependencies),
            '-Pament.build_tests=' + str(context.build_tests),
            '-Pament.package_manifest.name=' + context.package_manifest.name,
            '-Pament.exec_dependency_paths_in_workspace=' +
            ':'.join(context.exec_dependency_paths_in_workspace),
            '-Pament.gradle_recursive_dependencies=' + str(
                self._ament_gradle_recursive_dependencies(context)),
            '-Pament.gradle_isolated=' + str(context.ament_gradle_isolated),
        ]
        return cmd_args

    def _get_gradle_wrapper(self, context):
        gradlew_script = 'gradlew.bat' if IS_WINDOWS else 'gradlew'
        gradlew_path = os.path.join(context.source_space, gradlew_script)
        if os.path.isfile(gradlew_path):
            return gradlew_path

    def _get_gradle_executable(self, context):
        gradlew_path = self._get_gradle_wrapper(context)
        if gradlew_path:
            return gradlew_path

        gradle_script = 'gradle.bat' if IS_WINDOWS else 'gradle'
        if 'GRADLE_HOME' in os.environ:
            gradle_home = os.environ['GRADLE_HOME']
            gradle_path = os.path.join(gradle_home, 'bin', gradle_script)
            if os.path.isfile(gradle_path):
                return gradle_path
        gradle_path = shutil.which(gradle_script)
        if gradle_path:
            return gradle_path
        raise VerbExecutionError("Could not find 'gradle' executable")

    def prepare_arguments(self, parser):
        parser.add_argument(
            '--ament-gradle-args',
            nargs='*',
            default=[],
            help="Arbitrary arguments which are passed to 'ament_gradle' Gradle projects. "
            "Argument collection can be terminated with '--'.")

    def argument_preprocessor(self, args):
        # The ament CMake pass-through flag collects dashed options.
        # This requires special handling or argparse will complain about
        # unrecognized options.
        args, gradle_args = extract_argument_group(args, '--ament-gradle-args')
        extras = {'ament_gradle_args': gradle_args, }
        return args, extras

    def _prepare_cmd(self, context, gradle_task=None):
        cmd_args = self._get_ament_args(context)
        cmd_args += context.ament_gradle_args

        cmd = [self._get_gradle_executable(context)]
        cmd += cmd_args
        if gradle_task:
            cmd += [gradle_task]
        cmd += ['--stacktrace']

        return cmd

    def extend_context(self, options):
        ce = super(AmentGradleBuildType, self).extend_context(options)
        ament_gradle_args = list(options.ament_gradle_args)
        if not any([arg.startswith('-Pament.android_variant=') for arg in ament_gradle_args]):
            ament_gradle_args.append('-Pament.android_variant=release')
        ce.add('ament_gradle_args', ament_gradle_args)
        ce.add('ament_gradle_isolated', options.isolated)
        return ce

    def on_build(self, context):
        environment_hooks_path = os.path.join('share', context.package_manifest.name, 'environment')

        ext = '.sh' if not IS_WINDOWS else '.bat'
        # expand environment hook for AMENT_PREFIX_PATH
        ament_prefix_path_environment_hook = os.path.join(environment_hooks_path,
                                                          'ament_prefix_path' + ext)
        # expand environment hook for PATH
        path_environment_hook = os.path.join(environment_hooks_path, 'path' + ext)

        # expand environment hook for CLASSPATH
        classpath_filename = 'classpath' + ext
        template = get_environment_hook_classpath_template_path()

        # If using the Gradle Ament Plugin, JAR files are installed into
        # $AMENT_CURRENT_PREFIX/share/$PROJECT_NAME/java/$PROJECT_NAME.jar
        classpath = os.path.join('$AMENT_CURRENT_PREFIX', 'share', context.package_manifest.name,
                                 'java', context.package_manifest.name + ".jar")

        content = configure_string(template, {'_AMENT_EXPORT_JARS_CLASSPATH': classpath, })

        classpath_environment_hook = os.path.join(environment_hooks_path,
                                                  os.path.basename(classpath_filename))

        destination_path = os.path.join(context.build_space, classpath_environment_hook)
        destination_dir = os.path.dirname(destination_path)
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)
        with open(destination_path, 'w') as h:
            h.write(content)

        environment_hooks = [
            ament_prefix_path_environment_hook,
            classpath_environment_hook,
            path_environment_hook,
        ]

        # expand package-level setup files
        expand_package_level_setup_files(context, environment_hooks,
                                         environment_hooks_path)

        # remove anything that's on the destination tree but not in the source tree
        src_package_src_dir = os.path.join(context.source_space, 'src')
        dst_package_src_dir = os.path.join(context.build_space, 'src')

        src_dirnames, src_filenames = self._build_file_tree(src_package_src_dir)
        dst_dirnames, dst_filenames = self._build_file_tree(dst_package_src_dir)

        prune_dirnames = dst_dirnames - src_dirnames
        prune_filenames = dst_filenames - src_filenames

        for prune_filename in prune_filenames:
            os.remove(os.path.join(dst_package_src_dir, prune_filename))
        for prune_dirname in prune_dirnames:
            if os.path.exists(prune_dirname):
                shutil.rmtree(os.path.join(dst_package_src_dir, prune_dirname))

        # copy files from source_space to build_space to avoid poluting the latter
        # during the build process
        dir_util.copy_tree(context.source_space, context.build_space, update=1)

        yield BuildAction(
            self._prepare_cmd(
                context, gradle_task='assemble'), cwd=context.build_space)

    def on_test(self, context):
        yield BuildAction(self._prepare_cmd(context, gradle_task='test'), cwd=context.build_space)

    def on_install(self, context):
        # deploy package manifest
        deploy_file(
            context,
            context.source_space,
            'package.xml',
            dst_subfolder=os.path.join('share', context.package_manifest.name))

        # create marker file
        marker_file = os.path.join(context.install_space, 'share', 'ament_index', 'resource_index',
                                   'packages', context.package_manifest.name)
        if not os.path.exists(marker_file):
            marker_dir = os.path.dirname(marker_file)
            if not os.path.exists(marker_dir):
                os.makedirs(marker_dir)
            with open(marker_file, 'w'):  # "touching" the file
                pass

        ext = '.sh' if not IS_WINDOWS else '.bat'
        # deploy AMENT_PREFIX_PATH environment hook
        app_template_path = get_environment_hook_template_path('ament_prefix_path' + ext)
        deploy_file(
            context, os.path.dirname(app_template_path), os.path.basename(app_template_path),
            dst_subfolder=os.path.join('share', context.package_manifest.name, 'environment'))

        # deploy PATH environment hook
        path_template_path = get_environment_hook_template_path('path' + ext)
        deploy_file(
            context, os.path.dirname(path_template_path), os.path.basename(path_template_path),
            dst_subfolder=os.path.join('share', context.package_manifest.name, 'environment'))

        # deploy CLASSPATH environment hook
        destination_file = 'classpath' + ('.sh' if not IS_WINDOWS else '.bat')
        deploy_file(context, context.build_space,
                    os.path.join('share', context.package_manifest.name, 'environment',
                                 destination_file))

        # deploy package-level setup files
        for name in get_package_level_template_names():
            assert name.endswith('.in')
            deploy_file(context, context.build_space,
                        os.path.join('share', context.package_manifest.name, name[:-3]))

        yield BuildAction(
            self._prepare_cmd(
                context, gradle_task='assemble'), cwd=context.build_space)

    def on_uninstall(self, context):
        yield BuildAction(self._prepare_cmd(context, gradle_task='clean'), cwd=context.build_space)
