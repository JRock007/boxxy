"""
Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['main.py']

DATA_FILES = [('LICENSE'),
              ('ORIGINAL_LICENSE'),

              ('PodSixNet', ['PodSixNet/__init__.py']),
              ('PodSixNet', ['PodSixNet/async.py']),
              ('PodSixNet', ['PodSixNet/Channel.py']),
              ('PodSixNet', ['PodSixNet/Connection.py']),
              ('PodSixNet', ['PodSixNet/EndPoint.py']),
              ('PodSixNet', ['PodSixNet/rencode.py']),
              ('PodSixNet', ['PodSixNet/Server.py']),

              ('resources', ['resources/bar_done.png']),
              ('resources', ['resources/blueplayer.png']),
              ('resources', ['resources/gameover.png']),
              ('resources', ['resources/greenindicator.png']),
              ('resources', ['resources/greenplayer.png']),
              ('resources', ['resources/hoverline.png']),
              ('resources', ['resources/normalline.png']),
              ('resources', ['resources/redindicator.png']),
              ('resources', ['resources/score_panel.png']),
              ('resources', ['resources/separators.png']),
              ('resources', ['resources/youwin.png']),
              ('resources', ['resources/lose.wav']),
              ('resources', ['resources/music.wav']),
              ('resources', ['resources/place.wav']),
              ('resources', ['resources/win.wav'])]

OPTIONS = {'argv_emulation': False, 'iconfile': 'icon/icon.icns'}

setup(
    name="Boxxy",
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
