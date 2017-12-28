from distutils.core import setup

setup(
    name='SlackBotter',
    version='1.2',
    author='Stefan Finseth',
    author_email='stefanfinseth@gmail.com',
    packages=['slackbotter', 'dictstore', ],
    scripts=['bin/example.py',],
    url='http://github.com/sfinseth/SlackBotter.git',
    license='LICENSE.txt',
    description='Slack bot for simple workflow',
    long_description=open('README.txt').read(),
    requires=['slackclient', 'requests', ],
)
