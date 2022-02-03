import pathlib

from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="coinstac-computation",
    version="0.67",
    description="Generic computation implementation on COINSTAC.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/trendscenter/coinstac-computation",
    author="Aashis Khana1",
    author_email="sraashis@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    packages=[
        'coinstac_computation'
    ],
    include_package_data=True,
    install_requires=['coinstac']
)
