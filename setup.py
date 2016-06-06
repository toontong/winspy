#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Copyright 2016 chuantong.huang@163.com
Licensed under the Apache License 2.0
# 预设好参数，方便无参数直接运用 setup.py 即可.
# 建议使用 Python-2.6 32位 + py2exe
'''


import os
import shutil
from datetime import datetime
from distutils.core import setup

import py2exe, sys
path_join = os.path.join
currDir = os.path.dirname(__file__)


fp = open(path_join(currDir, 'version.py'), 'w+')
fp.write('''
VERSION = 'Version-0.0.1; build at %s'
''' % datetime.now())
fp.close()


# 预设好参数，方便无参数直接运用 setup.py 即可
sys.argv.append('py2exe')
sys.argv.append('--bundle-files')
sys.argv.append('1')
sys.argv.append('-c')
py2exe_options = {
    "includes":["sip", ],
}

class MyBuilder(object):
  def __init__(self, currDir, distDir):
    self.currDir = currDir
    self.distDir = distDir
    self._copy_dirs = []
    self._copy_files = []

  def _append_to(self, lst, src, dest):
    if dest is None: 
        dest = src
    if not os.path.isabs(src):
      src = path_join(self.currDir, src)
    dest = path_join(self.distDir, dest)
    lst.append((src, dest))

  def add_copy_dir(self, src, dest=None):
    self._append_to(self._copy_dirs, src, dest)

  def add_copy_file(self, src, dest=None):
    self._append_to(self._copy_files, src, dest)

  def build(self):
    f = "[* MyBuilder *]"
    for src, dest in self._copy_dirs:
      if not os.path.exists(dest):
        print f,'Copy-Dir from[%s] to [%s] finish.' % (src, dest)
        shutil.copytree(src, dest)
      else:
        print f, "Dir [%s] exists, do Nothing."% dest

    for src, dest in self._copy_files:
      if not os.path.exists(dest):
        print f, 'Copy-File from[%s] to [%s] finish.' % (src, dest)
        shutil.copy(src, dest)
      else:
        print f, "File [%s] exists, do Nothing." % dest



setup(
  console=[{"script":"main.py", 
    "icon_resources": [(1, './bulbs.ico')]}
  ],
  name='LedPlayer spyer ',
  description="this is a LedPlayer spyer",
  zipfile=None,
  options={'py2exe':py2exe_options},
)



