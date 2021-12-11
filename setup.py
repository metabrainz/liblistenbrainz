import setuptools
import pylistenbrainz

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pylistenbrainz",
    version=pylistenbrainz.__version__,
    author="Param Singh",
    author_email="iliekcomputers@gmail.com",
    description="A simple ListenBrainz client library for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/paramsingh/pylistenbrainz",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
    install_requires=[
        'requests >= 2.23.0',
    ],
)
