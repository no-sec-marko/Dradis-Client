import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dradis-client",
    version="1.0.0",
    author="Marko Winkler",
    author_email="mwinkler@omgwtfquak.de",
    description="Updated version of pydradis3 that was developed by GoVanguard",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/no-sec-marko/dradis-client",
    packages=['dradis'],
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent',
    ),
)
