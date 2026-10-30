from setuptools import find_packages, setup

setup(
    name="solar-monitoring-backend",
    version="1.0.0",
    description="Back-End (Flask + MySQL) для БД solar_monitoring",
    packages=find_packages(exclude=("tests",)),
    package_data={"my_project": ["ui/*"]},
    python_requires=">=3.9",
    install_requires=[
        "Flask>=3.0",
        "PyMySQL>=1.1",
        "cryptography>=42.0",
        "PyYAML>=6.0",
    ],
)
