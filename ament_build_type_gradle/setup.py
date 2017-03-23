import os

from setuptools import find_packages
from setuptools import setup
from setuptools.command.build_py import build_py
from distutils.command.install_data import install_data

IS_WINDOWS = os.name == 'nt'


class ament_index_generator(install_data):
    def run(self):
        super().run()
        target_dir = os.path.join(self.install_dir, 'share', 'ament_index',
                                  'resource_index', 'templates')
        template_filename = 'classpath' + ('.sh.in'
                                           if not IS_WINDOWS else '.bat.in')
        template_path = os.path.join(self.install_dir, 'share',
                                     'ament_build_type_gradle', 'template',
                                     'environment_hook', template_filename)

        self.mkpath(target_dir)
        with open(
                os.path.join(target_dir, 'ament_build_type_gradle_classpath'),
                'w') as f:
            f.write(template_path)


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
    data_files=[('share/ament_build_type_gradle/template/environment_hook', [
        'ament_build_type_gradle/template/environment_hook/classpath.sh.in',
        'ament_build_type_gradle/template/environment_hook/classpath.bat.in',
    ])],
    cmdclass={'install_data': ament_index_generator})
