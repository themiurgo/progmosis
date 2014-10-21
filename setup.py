from setuptools import setup, find_packages
import progmosis
setup(
    name = "progmosis",
    version = progmosis.__version__,
    description="Individual risk-assessment for disease outbreaks from CDRs",
    url='https://github.com/themiurgo/progmosis',
    author="Antonio Lima",
    author_email="anto87@gmail.com",
    license=progmosis.__license__,
    packages = find_packages(),
    install_requires=[
       'docopt>=0.6.1',
    ],
    entry_points={
        'console_scripts': [
            'progmosis=progmosis:main',
        ],
    },
)
