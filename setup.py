# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

required_packages = open('requirements.txt', 'r').readlines()

setup(name='paperwaster',
    version='0.0.1',
    description='wastes paper',
    packages=find_packages(),
    install_requires=required_packages,
    entry_points={
        'console_scripts': [
            'paperw=paperwaster.cli.paperw:main',
            'remote-print=paperwaster.cli.remote_print:main',
            'text2img=paperwaster.cli.text2img:main',
            'paperirc=paperwaster.ircbot:main',
        ]
    },
    include_package_data=True,
)
