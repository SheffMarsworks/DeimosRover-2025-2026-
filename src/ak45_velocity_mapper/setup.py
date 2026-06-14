from glob import glob
from setuptools import find_packages, setup

package_name = 'ak45_velocity_mapper'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='robot',
    maintainer_email='robot@todo.todo',
    description='Convert diff-drive cmd_vel into 4 wheel velocity controller commands.',
    license='TODO',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'diff_to_velocity = ak45_velocity_mapper.diff_to_velocity:main',
        ],
    },
)
