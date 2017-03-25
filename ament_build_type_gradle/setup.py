import os

from setuptools import find_packages
from setuptools import setup
from setuptools.command.install import install
from setuptools.command.develop import develop

IS_WINDOWS = os.name == 'nt'

# Customize both the install (non-symlinked) and develop (symlinked) commands so that we can
# install an entry in the ament index for the path to the CLASSPATH templates


class ament_gradle_install(install):
    def run(self):
        super().run()
        install_dir = self.prefix
        install_index_dir = os.path.join(install_dir, 'share', 'ament_index',
                                         'resource_index', 'templates')
        install_index_path = os.path.join(install_index_dir,
                                          'ament_build_type_gradle_classpath')

        install_lib_dir = self.get_finalized_command('install_lib').install_dir

        template_dir = os.path.join(install_lib_dir, 'ament_build_type_gradle',
                                    'template', 'environment_hook')
        template_filename = 'classpath' + ('.sh.in'
                                           if not IS_WINDOWS else '.bat.in')
        template_path = os.path.join(template_dir, template_filename)

        self.mkpath(install_index_dir)
        with open(install_index_path, 'w') as f:
            f.write(template_path)


class ament_gradle_develop(develop):
    def run(self):
        super().run()
        build_dir = os.path.abspath(self.setup_path)
        src_dir = os.path.dirname(
            os.path.realpath(os.path.join(build_dir, 'setup.py')))
        install_dir = self.prefix

        template_dir = os.path.join(src_dir, 'ament_build_type_gradle',
                                    'template', 'environment_hook')
        template_filename = 'classpath' + ('.sh.in'
                                           if not IS_WINDOWS else '.bat.in')
        template_path = os.path.join(template_dir, template_filename)

        build_index_dir = os.path.join(build_dir, 'share', 'ament_index',
                                       'resource_index', 'templates')
        build_index_path = os.path.join(build_index_dir,
                                        'ament_build_type_gradle_classpath')
        self.mkpath(build_index_dir)
        with open(build_index_path, 'w') as f:
            f.write(template_path)

        install_index_dir = os.path.join(install_dir, 'share', 'ament_index',
                                         'resource_index', 'templates')
        install_index_path = os.path.join(install_index_dir,
                                          'ament_build_type_gradle_classpath')
        self.mkpath(install_index_dir)

        if os.path.exists(install_index_path):
            os.remove(install_index_path)
        if not os.path.exists(install_index_path):
            os.symlink(build_index_path, install_index_path)


setup(
    name='ament_build_type_gradle',
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    install_requires=['ament-package', 'osrf_pycommon'],
    author='Esteve Fernandez',
    author_email='esteve@apache.org',
    maintainer='Esteve Fernandez',
    maintainer_email='esteve@apache.org',
    keywords=['ROS'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    description='Gradle tool support for ament.',
    license='Apache License, Version 2.0',
    test_suite='test',
    entry_points={
        'ament.build_types':
        ['ament_gradle = ament_build_type_gradle:AmentGradleBuildType', ],
    },
    package_data={
        'ament_build_type_gradle': ['template/environment_hook/*.in']
    },
    cmdclass={
        'develop': ament_gradle_develop,
        'install': ament_gradle_install,
    }, )
