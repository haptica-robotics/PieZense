# !/usr/bin/env python3

import setuptools

with open("README.md", "r") as fh:
    description = fh.read()

setuptools.setup(
    name="piezense",
    version="0.0.4",
    author="Haptica Robotics",
    author_email="info@hapticarobotics.com",
    packages=["piezense"],
    description="A Python package for interfacing with PieZense pneumatic systems",
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://github.com/haptica-robotics/piezense",
    license='LicenseRef-Proprietary',
    python_requires='>=3.8',
    install_requires=["bleak==1.1.1"]
)

