import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pydradis3",
    version="0.2.1",
    author="Shane Scott",
    author_email="sscott@gvit.com",
    description="Update of pydradis for Python3 plus some optimizations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GoVanguard/pydradis3",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: GPLv2 License",
        "Operating System :: OS Independent",
    ),
)
