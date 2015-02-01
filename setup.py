#!/usr/bin/env python3
"""Leavitt: command line tool and library for fitting Leavitt's Law.

Leavitt is a command line tool and Python library for fitting Leavitt's Law
to variable star data.
"""

DOCLINES = __doc__.split("\n")

CLASSIFIERS = """\
Programming Language :: Python
Programming Language :: Python :: 3
Intended Audience :: Science/Research
License :: OSI Approved :: MIT License
Operating System :: OS Independent
Topic :: Scientific/Engineering :: Astronomy
Topic :: Software Development :: Libraries :: Python Modules
"""

MAJOR   = 0
MINOR   = 1
MICRO   = 0
VERSION = "%d.%d.%d" % (MAJOR, MINOR, MICRO)

def setup_package():
    metadata = dict(
        name = "leavitt",
        url = "https://github.com/astroswego/leavitt",
        description = DOCLINES[0],
        long_description = "\n".join(DOCLINES[2:]),
        version = VERSION,
        package_dir = {"" : "src"},
        packages = ["leavitt"],
        entry_points = {
            "console_scripts": [
                "leavitt = leavitt.leavitt:main"
            ]
        },
        keywords = [
            "astronomy"
            "variable star"
            "leavitt's law"
        ],
        classifiers = [f for f in CLASSIFIERS.split("\n") if f],
        requires = [
            "numpy (>= 1.8.0)"
        ]
    )

    from setuptools import setup

    setup(**metadata)

if __name__ == "__main__":
    setup_package()
