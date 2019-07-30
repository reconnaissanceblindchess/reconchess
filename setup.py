import setuptools

with open('requirements.txt') as fp:
    requirements = fp.readlines()

with open('README.rst') as fp:
    long_description = fp.read()

setuptools.setup(
    name='reconchess',
    version='1.3.5',
    author='Johns Hopkins University Applied Physics Laboratory',
    description='A python package for building Reconnaissance Chess players',
    long_description=long_description,
    long_description_content_typ='text/x-rst',
    url='https://github.com/reconnaissanceblindchess/reconchess',
    packages=['reconchess', 'reconchess.scripts', 'reconchess.bots'],
    package_data={'reconchess': ['res/white/*.png', 'res/black/*.png']},
    entry_points={
        'console_scripts': [
            'rc-bot-match=reconchess.scripts.rc_bot_match:main',
            'rc-play=reconchess.scripts.rc_play:main',
            'rc-replay=reconchess.scripts.rc_replay:main',
            'rc-playback=reconchess.scripts.rc_playback:main',
            'rc-register=reconchess.scripts.rc_register:main',
            'rc-connect=reconchess.scripts.rc_connect:main',
            'rc-play-on-server=reconchess.scripts.rc_play_on_server:main',
        ],
    },
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
