import os
import sys
from setuptools import find_packages, setup

setup(
    name="cdp",
    version="1.2.0",
    author="Zeshawn Shaheen, Charles Doutriaux",
    author_email="shaheen2@llnl.gov, doutriaux1@llnl.gov",
    description="Framework for creating scientific diagnostics.",
    packages=find_packages(exclude=["*.test", "*.test.*", "test.*", "test"]),
    data_files=[(os.path.join(sys.prefix,'share','cdp'), ('share/default_args.json',))],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'cdp-distrib=cdp.cli.cdp_distrib:main'
        ]}
)
