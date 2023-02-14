from setuptools import setup

setup(
    name='cmscheck',
    version='1.0',
    requires=[
        'requests',
    ],
    author='Marvin Roßkothen',
    description='Prüfe, ob und welches CMS auf einer Website installiert ist.',
    entry_points={
        'console_scripts': [
            'cmscheck=cmsCheck:main'
        ]
    }
)