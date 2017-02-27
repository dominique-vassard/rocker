from setuptools import setup, find_packages

setup(
    name="rocker",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=['Click',
                      'request'
                      ],
    entry_points='''
    [console_scripts]
    rocker=rocker.rocker:rocker
    '''
)