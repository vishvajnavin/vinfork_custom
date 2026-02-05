from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

from vinfork_custom import __version__ as version

setup(
	name="vinfork_custom",
	version=version,
	description="Legacy setup for Frappe Cloud compatibility",
	author="vishvaj navin",
	author_email="vishvaj25252@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
