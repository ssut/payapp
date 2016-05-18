from os import path
from setuptools import setup, find_packages

import payapp

base_dir = path.dirname(__file__)
requirements_path = path.join(base_dir, 'requirements.txt')
install_requires = map(str.strip, open(requirements_path).readlines())

version = payapp.__version__
desc = payapp.__doc__

setup(
    name='payapp',
    version=version,
    description=desc,
    long_description=desc,
    author='SuHun Han (ssut)',
    author_email='ssut@ssut.me',
    url='https://github.com/ssut/payapp',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: Freeware',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    packages=find_packages(),
    install_requires=install_requires
)