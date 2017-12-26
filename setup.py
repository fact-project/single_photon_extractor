from distutils.core import setup

setup(
    name='single_photon_extractor',
    version='0.0.1',
    description='A sandbox to explore single photon extraction',
    url='https://github.com/fact-project/',
    author='Sebastian Achim Mueller',
    author_email='sebmuell@phys.ethz.ch',
    license='GPLv3',
    packages=[
        'single_photon_extractor',
        'single_photon_extractor.air_shower_classification',
    ],
    package_data={
        'single_photon_extractor': []
    },
    install_requires=[
        'docopt',
        'scipy',
        'matplotlib',
        'pyfact',
        'pandas',
    ],
    entry_points={'console_scripts': []},
    zip_safe=False,
)
