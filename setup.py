from setuptools import setup, find_packages
from codecs import open
from os import path
import re

version_file = "junglebook/__version__.py"
verstrline = open(version_file, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (version_file,))

here = path.abspath(path.dirname(__file__))

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("test-requirements.txt") as f:
    test_requirements = f.read().splitlines()

setup_args = dict(
    name="junglebook",
    version=verstr,
    description="Jungle Book",
    url="https://gitlab.com/jungleai/appliedml/junglebook",
    author="Jungle",
    author_email="dev@jungle.ai",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(exclude=["contrib", "docs"]),
    install_requires=requirements,
    tests_require=test_requirements,
    entry_points={
        "console_scripts": [
            "junglebook=junglebook.main.00_Configuration:entry_point",
        ],
    },
)

if __name__ == "__main__":
    setup(**setup_args)
