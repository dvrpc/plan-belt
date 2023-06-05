from setuptools import find_packages, setup

setup(
    name="planbelt",
    version="0.4.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Click",
    ],
    entry_points={
        "console_scripts": [
            "conflate = plan_belt.cli:conflation",
            "synchrosum = plan_belt.cli:synchro",
            "synchrosim = plan_belt.cli:sim",
        ]
    },
)
