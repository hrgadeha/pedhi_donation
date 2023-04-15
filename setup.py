from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in pedhi_donation/__init__.py
from pedhi_donation import __version__ as version

setup(
	name="pedhi_donation",
	version=version,
	description="App to Manage Amount split into cost center",
	author="Hardik Gadesha",
	author_email="hardikgadesha@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
