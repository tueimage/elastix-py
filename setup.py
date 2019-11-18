import setuptools


setuptools.setup(
    name="elastix-py",
    version="0.0.1",
    author="Koen A. J. Eppenhof",
    author_email="k.a.j.eppenhof@tue.nl",
    description="A Python wrapper for the Elastix image registration software package.",
    long_description="""
This package provides a thin wrapper that allows you to call Elastix and Transformix from Python.""",
    long_description_content_type="text/markdown",
    url="https://github.com/tueimage/elastix-py",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
