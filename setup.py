import setuptools

with open('requirements.txt') as fp:
    requirements = fp.readlines()

setuptools.setup(
    name='python-rbmc',
    version='0.1',
    packages=['rbmc', 'rbmc_server'],
    package_data={'rbmc': ['res/white/*.png', 'res/black/*.png']},
    scripts=['scripts/rbmc-bot-match.py', 'scripts/rbmc-connect.py', 'scripts/rbmc-play.py', 'scripts/rbmc-replay.py'],
    install_requires=requirements,
)
