import os

from setuptools import find_packages
from setuptools import setup

package_name = 'ament_build_type_gradle'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/' + package_name, ['package.xml']),
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
    ],
    install_requires=['ament-package', 'osrf_pycommon'],
    zip_safe=True,
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
        'ament.build_types': [f'ament_gradle = {package_name}:AmentGradleBuildType', ],
    },
    package_data={f'{package_name}': ['template/environment_hook/*.in']}, )
