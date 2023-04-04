from setuptools import find_packages, setup

setup(
    name="planbelt",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Click",
    ],
    entry_points={
        "console_scripts": ["conflate = plan_belt.cli:main"],
    },
)