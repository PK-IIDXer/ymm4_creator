from setuptools import find_packages, setup

setup(
    name="ymm4creator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "setuptools>=56.0.0",
    ],
    python_requires=">=3.9",
    setup_requires=[
        "setuptools>=56.0.0",
    ],
    package_data={
        "": ["py.typed"],
    },
)
