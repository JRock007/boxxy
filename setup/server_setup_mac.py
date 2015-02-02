"""
Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['server.py']

DATA_FILES = [('LICENSE'),
              ('ORIGINAL_LICENSE'),

              ('PodSixNet', ['PodSixNet/__init__.py']),
              ('PodSixNet', ['PodSixNet/async.py']),
              ('PodSixNet', ['PodSixNet/Channel.py']),
              ('PodSixNet', ['PodSixNet/Connection.py']),
              ('PodSixNet', ['PodSixNet/EndPoint.py']),
              ('PodSixNet', ['PodSixNet/rencode.py']),
              ('PodSixNet', ['PodSixNet/Server.py'])]

OPTIONS = {'argv_emulation': False, 'iconfile': 'icon_server/icon.icns'}

setup(
    name="Boxxy server",
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
