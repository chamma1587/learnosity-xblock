"""Setup for learnosity XBlock."""


import os

from setuptools import setup


def package_data(pkg, roots):
    """Generic function to find package_data.

    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.

    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


setup(
    name='learnosity-xblock',
    version='0.1',
    description='learnosity XBlock', 
    license='UNKNOWN', 
    packages=[
        'learnosityx',
    ],
    install_requires=[
        'XBlock',
        'learnosity-sdk',
    ],
    entry_points={
        'xblock.v1': [
            'learnosityx = learnosity:LearnosityXBlock',
        ]
    },
    package_data=package_data("learnosityx", ["static", "public"]),
)
