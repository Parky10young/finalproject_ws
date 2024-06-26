from setuptools import setup
import os
from glob import glob

package_name = 'tracking_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*')))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='yahboom',
    maintainer_email='brandonfang412@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'Tracjectory_node = tracking_control.Tracjectory_plan:main',
            'joy_safety_ctrl = tracking_control.joy_safety_ctrl:main',
            'visualization = tracking_control.visualize_path:main',
            'action_node = tracking_control.robot_action:main',
        ],
    },
)
