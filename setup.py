import sys

from setuptools import find_packages
from setuptools import setup

assert sys.version_info[0] == 3 and sys.version_info[1] >= 6, "Hive Plug & Play (HAF) requires Python 3.6 or newer"

setup(
    name='haf_plug_play',
    version='0.3.1',
    description='Customizable streaming and parsing microservice for custom_json ops on Hive.',
    long_description=open('README.md').read(),
    packages=find_packages(exclude=['scripts']),
    install_requires=[
        'psycopg2',
        'requests',
        'aiohttp',
        'jsonrpcserver'
    ],
    entry_points = {
        'console_scripts': [
            'haf_plug_play = haf_plug_play.run_plug_play:run'
        ]
    }
)