import setuptools

with open('requirements.txt') as fp:
    requirements = fp.readlines()

setuptools.setup(
    name='python-rbmc',
    version='0.1',
    packages=['rbmc', 'rbmc_server', 'rbmc.scripts', 'rbmc.baselines'],
    package_data={'rbmc': ['res/white/*.png', 'res/black/*.png']},
    scripts=[
        'rbmc/scripts/rbmc-bot-match.py',
        'rbmc/scripts/rbmc-connect.py',
        'rbmc/scripts/rbmc-play.py',
        'rbmc/scripts/rbmc-replay.py'
    ],
    install_requires=requirements,
)
