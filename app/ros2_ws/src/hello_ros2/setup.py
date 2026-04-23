from setuptools import setup

package_name = 'hello_ros2'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='devops',
    description='ROS2 demo package',
    entry_points={
        'console_scripts': [
            'talker = hello_ros2.talker:main',
            'listener = hello_ros2.listener:main',
        ],
    },
)