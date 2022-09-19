# python pyslib setup.py
import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='pyslib',
    version='0.2',
    author='Sheng Tian',
    author_email='ts0110@atmos.ucla.edu',
    description='A Python library for space physics research',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/tsssss/pyslib',
    requires=['numpy','matplotlib','requests','cdflib','spacepy','pyspedas','pytplot'],
    platforms=['Mac OS'],
    license='MIT',
    packages=setuptools.find_packages(),
    package_data={'':['*.py','*.md']},
    classifiers= [
        'Programming Language :: Python :: 3',
        'Operating System :: MacOS',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering :: Physics'
    ],
)