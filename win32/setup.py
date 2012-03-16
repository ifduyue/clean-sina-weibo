#-*- coding:utf8 -*-
from distutils.core import setup
import py2exe

setup(
    name = u'新浪微博清理器',
    description = u'lyxint.com',
    version = u"20120223",

    windows = [
                  {
                      'script': 'clean-sina-weibo-win32.py',
                      'icon_resources': [(1, "icon.ico")],
                  }
              ],

    options = {
                  'py2exe': {
                      'packages':'encodings',
                      'includes': 'cairo,pango,gio,pangocairo,atk',
                      'excludes': 'sets',
                  }
              },
)
