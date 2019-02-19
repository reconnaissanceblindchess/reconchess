import setuptools

with open('requirements.txt') as fp:
    requirements = fp.readlines()

with open('README.rst') as fp:
    long_description = fp.read()

setuptools.setup(
    name='reconchess',
    version='0.0.1',
    author='Johns Hopkins University Applied Physics Laboratory',
    description='A python package for building Reconnaissance Chess players',
    long_description=long_description,
    long_description_content_typ='text/x-rst',
    url='https://github.com/reconnaissanceblindchess/reconchess',
    packages=['reconchess', 'reconchess_server', 'reconchess.scripts', 'reconchess.baselines'],
    package_data={'reconchess': ['res/white/*.png', 'res/black/*.png']},
    scripts=[
        'reconchess/scripts/rc-bot-match.py',
        'reconchess/scripts/rc-connect.py',
        'reconchess/scripts/rc-play.py',
        'reconchess/scripts/rc-replay.py'
    ],
    python_requires='>=3.5',
    install_requires=requirements,
    project_urls={
        'Documentation': 'https://reconchess.readthedocs.io/en/latest/index.html',
        'Source': 'https://github.com/reconnaissanceblindchess/reconchess',
        'Tracker': 'https://github.com/reconnaissanceblindchess/reconchess/issues',
    },
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Games/Entertainment :: Board Games',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries',
    ],
)
