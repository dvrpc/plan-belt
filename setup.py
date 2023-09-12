from setuptools import find_packages, setup

setup(
    name="planbelt",
    version="0.5.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Click",
        "geopandas",
        "pandas",
        "matplotlib",
        "pg-data-etl @ git+https://github.com/mmorley0395/pg-data-etl",
        "psycopg2-binary",
        "python-dotenv",
        "sqlalchemy",
        "geoalchemy2",
    ],
    entry_points={
        "console_scripts": [
            "conflate = plan_belt.cli:conflation",
            "synchrosum = plan_belt.cli:synchro",
            "synchrosim = plan_belt.cli:sim",
        ]
    },
)
