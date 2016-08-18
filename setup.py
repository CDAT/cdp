from setuptools import find_packages, setup

print find_packages()
print '--------------'
setup(
    name="CDP",
    version="0.1a",
    author="Zeshawn Shaheen",
    author_email="shaheen2@llnl.gov",
    description="Framework for creating climate diagnostics.",
    #packages=find_packages(),
    packages=['CDP', 'PMP'],
    include_package_data=True
    #scripts = ['base/CDPDriver.py']
)
