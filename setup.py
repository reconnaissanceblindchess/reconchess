import setuptools

with open('requirements.txt') as fp:
    requirements = fp.readlines()

setuptools.setup(
    name='reconchess',
    version='0.1',
    packages=['reconchess', 'reconchess_server', 'reconchess.scripts', 'reconchess.baselines'],
    package_data={'reconchess': ['res/white/*.png', 'res/black/*.png']},
    scripts=[
        'reconchess/scripts/rc-bot-match.py',
        'reconchess/scripts/rc-connect.py',
        'reconchess/scripts/rc-play.py',
        'reconchess/scripts/rc-replay.py'
    ],
    install_requires=requirements,
)
