import setuptools

with open('requirements.txt') as fp:
    requirements = fp.readlines()

setuptools.setup(
    name='reconchess',
    version='0.1',
    packages=['reconchess', 'reconchess_server', 'reconchess.scripts', 'reconchess.baselines'],
    package_data={'reconchess': ['res/white/*.png', 'res/black/*.png']},
    scripts=[
        'reconchess/scripts/reconchess-bot-match.py',
        'reconchess/scripts/reconchess-connect.py',
        'reconchess/scripts/reconchess-play.py',
        'reconchess/scripts/reconchess-replay.py'
    ],
    install_requires=requirements,
)
