# Copyright 2014 Open Source Robotics Foundation, Inc.
# Copyright 2016 Esteve Fernandez <esteve@apache.org>
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

"""Implements the BuildType support for gradle based ament packages."""

import os
import shutil

from ament_tools.helper import extract_argument_group

from ament_tools.build_type import BuildAction
from ament_tools.build_type import BuildType

IS_WINDOWS = os.name == 'nt'

def get_gradle_executable():
    gradle_script = 'gradle.bat' if IS_WINDOWS else 'gradle'
    if 'GRADLE_HOME' in os.environ:
        gradle_home = os.environ['GRADLE_HOME']
        gradle_path = os.path.join(gradle_home, 'bin', gradle_script)
        if os.path.isfile(gradle_path):
            return gradle_path
    return shutil.which(gradle_script)


GRADLE_EXECUTABLE = get_gradle_executable()


class AmentGradleBuildType(BuildType):
    build_type = 'ament_gradle'
    description = "ament package built with Gradle"

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
        extras = {
            'ament_gradle_args': gradle_args,
        }
        return args, extras

    def extend_context(self, options):
        ce = super(AmentGradleBuildType, self).extend_context(options)
        ce.add('ament_gradle_args', options.ament_gradle_args)
        return ce

    def on_build(self, context):
        cmd_args = [
            '-Pament.build_space=' + context.build_space,
            '-Pament.install_space=' + context.install_space,
            '-Pament.dependencies=' + ':'.join(context.build_dependencies),
            '-Pament.build_tests=' + str(context.build_tests),
        ]
        cmd_args += context.ament_gradle_args

        cmd = [GRADLE_EXECUTABLE]
        cmd += cmd_args
        cmd += ['assemble']

        yield BuildAction(cmd, cwd=context.source_space)

    def on_test(self, context):
        cmd_args = [
            '-Pament.build_space=' + context.build_space,
            '-Pament.install_space=' + context.install_space,
            '-Pament.dependencies=' + ':'.join(context.build_dependencies),
            '-Pament.build_tests=' + str(context.build_tests),
        ]
        cmd_args += context.ament_gradle_args

        cmd = [GRADLE_EXECUTABLE]
        cmd += cmd_args
        cmd += ['test']

        yield BuildAction(cmd, cwd=context.source_space)

    def on_install(self, context):
        cmd_args = [
            '-Pament.build_space=' + context.build_space,
            '-Pament.install_space=' + context.install_space,
            '-Pament.dependencies=' + ':'.join(context.build_dependencies),
            '-Pament.build_tests=' + str(context.build_tests),
        ]

        cmd_args += context.ament_gradle_args

        cmd = [GRADLE_EXECUTABLE]
        cmd += cmd_args
        cmd += ['assemble']

        yield BuildAction(cmd, cwd=context.source_space)

    def on_uninstall(self, context):
        cmd_args = [
            '-Pament.build_space=' + context.build_space,
            '-Pament.install_space=' + context.install_space,
            '-Pament.dependencies=' + ':'.join(context.build_dependencies),
            '-Pament.build_tests=' + str(context.build_tests),
        ]

        cmd_args += context.ament_gradle_args

        cmd = [GRADLE_EXECUTABLE]
        cmd += cmd_args
        cmd += ['clean']

        yield BuildAction(cmd, cwd=context.source_space)
