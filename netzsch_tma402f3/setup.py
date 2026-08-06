#! THIS setup.py IS MADE FROM THE TEMPLATE IN THE LINK BELOW

from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup

d = generate_distutils_setup(
    packages=['netzsch_tma402f3'],
    package_dir={'': 'src'}
)

setup(**d)
