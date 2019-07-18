# from distutils.core import setup
from setuptools import setup

setup(
    name='SlackBotter',
    version='1.2.7',
    author='Stefan Finseth',
    author_email='stefanfinseth@gmail.com',
    packages=['slackbotter'],
    scripts=['bin/example.py', ],
    url='http://github.com/sfinseth/SlackBotter.git',
    license='LICENSE.txt',
    description='Slack bot for simple workflow',
    long_description=open('README.md').read(),
    requires=['slackclient', 'requests', ],
)
