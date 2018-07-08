try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

config = {
        'name': 'slib',
        'version': '0.1',
        'description': 'A Python Library on space physics research',
        'author': 'Sheng Tian',
        'url': '',
        'download_url': '', 
        'author_email': 'tianx138@umn.edu',
        'packages': find_packages(),
        'install_requires': ['numpy','matplotlib','requests','cdflib'],
        }

setup(**config)
