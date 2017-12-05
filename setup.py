from setuptools import setup, find_packages
from pip.req import parse_requirements

reqs = [str(req.req) for req in parse_requirements("requirements.txt", session=False)]

setup(
    name='dynsync',
    version='0.0.1',
    description='Dynamic (inotify) two-way synchronization tool.',
    author='Marek Jarycki',
    url='http://github.com/emdej/dynsync',
    keywords='sync rsync inotify auto file synchronization two-way',
    platforms=['linux'],
    license='GPLv2',
    install_requires=reqs,
    packages=find_packages(),
    package_files=[("", ["requirementx.txt"])],
    entry_points={
        'console_scripts': [
            'dynsync=dynsync.dynsync:main',
        ],
    },
    zip_safe=False,
)
