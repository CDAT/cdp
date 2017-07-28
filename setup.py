from setuptools import find_packages, setup

setup(
    name="cdp",
    version="1.0.3",
    author="Zeshawn Shaheen",
    author_email="shaheen2@llnl.gov",
    description="Framework for creating scientific diagnostics.",
    packages=find_packages(exclude=["*.test", "*.test.*", "test.*", "test"]),
    include_package_data=True,
    scripts = ["scripts/cdp_manage"]
)
