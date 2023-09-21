from setuptools import find_packages, setup

setup(
    name="planbelt",
    version="0.5.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Click",
        "geopandas",
        "pg-data-etl @ git+https://github.com/mmorley0395/pg-data-etl",
        "python-dotenv",
        "sqlalchemy",
        "backports.functools-lru-cache",
        "brotli",
        "folium",
        "geoalchemy2",
        "geopandas",
        "ipykernel",
        "mapclassify",
        "matplotlib",
        "munch",
        "munkres",
        "openpyxl",
        "pooch",
        "psycopg2-binary",
        "pysocks",
        "python-dotenv",
        "rtree",
        "ukkonen",
        "xlsxwriter",
        "xyzservices",
    ],
    entry_points={
        "console_scripts": [
            "conflate = plan_belt.cli:conflation",
            "synchrosum = plan_belt.cli:synchro",
            "synchrosim = plan_belt.cli:sim",
        ]
    },
)
