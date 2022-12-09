#!/usr/bin/env python

import os
import re
from glob import glob
from os.path import basename, splitext

from setuptools import find_packages, setup  # type: ignore

NAME = "contaxy"
MAIN_PACKAGE = NAME  # Change if main package != NAME
DESCRIPTION = "Python package template."
URL = "https://github.com/ml-tooling/contaxy"
EMAIL = "team@mltooling.org"
AUTHOR = "ML Tooling Team"
LICENSE = "MIT"
REQUIRES_PYTHON = ">=3.8"
VERSION = None  # Only set version if you like to overwrite the version in _about.py

PWD = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
try:
    with open(os.path.join(PWD, "README.md"), encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = ""

# Extract the version from the _about.py module.
if not VERSION:
    try:
        with open(os.path.join(PWD, "src", MAIN_PACKAGE, "_about.py")) as f:  # type: ignore
            VERSION = re.findall(r"__version__\s*=\s*\"(.+)\"", f.read())[0]
    except FileNotFoundError:
        VERSION = "0.0.0"

# Where the magic happens:
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    license=LICENSE,
    packages=find_packages(where="src", exclude=("tests", "test", "examples", "docs")),
    package_dir={"": "src"} if os.path.exists("src") else {},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    zip_safe=False,
    install_requires=[
        "typer",  # TODO: remove typer?
        "pydantic[dotenv,email]",
        "fastapi==0.75.2",
        "requests",
        # Better logging
        "loguru",
        "filetype",
        "addict",
        "requests-toolbelt",
        "shortuuid",
        "slugify",
    ],
    # deprecated: dependency_links=dependency_links,
    extras_require={
        "server": [
            # Add all the runtime requirements here:
            "kubernetes",
            "docker",
            # TODO: Dev only - timing
            "fastapi-utils",
            # Required by fastapi.security OAuth2PasswordBearer & fastapi.UploadFile for example
            "python-multipart",
            # Used for multipart stream parsing in file manager
            "streaming_form_data",
            "psutil",
            "uvicorn",
            "sqlalchemy>=1.4.0",
            # Postgres Driver
            "psycopg2",
            # Generates concise, unambiguous, URL-safe UUIDs.
            "shortuuid",
            # Create slugs from unicode strings
            "python-slugify",
            # Used in MinioFileManager
            "minio",
            # Used in AzureBlobFileManager
            "azure-storage-blob",
            # Used for jwt handling
            "python-jose[cryptography]",
            # Used for password hashing
            "passlib[bcrypt]",
            # TODO: FOR in-memory dict db: Merge dictionaries via json merge patch
            "json-merge-patch",
            # TODO: FOR in-memory dict db: Merge dictionaries via json merge patch
            "jsonpath-ng",
            # TODO: Improve
            "jinja2",
            # Used for OIDC handling
            "requests_oauthlib",
            # Create fake data for testing
            "faker",
        ],
        "dev": [
            "setuptools",
            "wheel",
            "twine",
            "flake8",
            "pytest",
            "pytest-mock",
            "pytest-cov",
            "mypy",
            "types-python-slugify",
            "types-requests",
            "types-cachetools",
            "black",
            "pydocstyle",
            "isort",
            "lazydocs",
            "locust",
            # Test profiling
            "pyinstrument",
            # Export profiling information about the tests
            "pytest-profiling",
            # For better print debugging via debug
            "devtools[pygments]",
            # For Jupyter Kernel support
            "ipykernel",
            # TODO: Move to required when necessary
            "universal-build",
            "requests",
        ],
    },
    setup_requires=['wheel'],
    include_package_data=True,
    package_data={
        # If there are data files included in your packages that need to be
        # 'sample': ['package_data.dat'],
        "contaxy.api.endpoints": ["templates/*"]
    },
    classifiers=[
        # TODO: Update based on https://pypi.org/classifiers/
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering",
        "Topic :: Utilities",
    ],
    project_urls={
        "Changelog": URL + "/releases",
        "Issue Tracker": URL + "/issues",
        "Documentation": URL + "#documentation",
        "Source": URL,
    },
    entry_points={"console_scripts": [f"{NAME}={MAIN_PACKAGE}._cli:cli"]},
    keywords=[
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
)
