from glob import glob
import os
from setuptools import find_packages, setup

package_name = "rover_tapocam"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        (
            "share/ament_index/resource_index/packages",
            ["resource/" + package_name],
        ),
        (os.path.join("share", package_name), ["package.xml"]),
        (os.path.join("share", package_name, "config"), glob("config/*.yaml")),
    ],
    install_requires=[
        "setuptools",
        "onvif-zeep",
        "pytapo",
        "opencv-python",
    ],
    zip_safe=True,
    maintainer="yankikirlikova",
    maintainer_email="yankikirlikova@users.noreply.github.com",
    description="Tapo camera control and capture tools for Deimos rover workflows.",
    license="MIT",
    extras_require={"test": ["pytest"]},
    entry_points={
        "console_scripts": [
            "tapo_take_photos = rover_tapocam.tapo_take_photos:main",
            "tapo_panoramic = rover_tapocam.panoramic:main",
            "tapo_ptz_wasd = rover_tapocam.ptz_wasd:main",
            "tapo_cli = rover_tapocam.python_tapo_cli:main",
            "tapo_onvif_test = rover_tapocam.onvif_test:main",
            "tapo_onvif_set_encoder = rover_tapocam.onvif_set_encoder:main",
            "tapo_onvif_dump_options = rover_tapocam.onvif_dump_options:main",
        ],
    },
)
