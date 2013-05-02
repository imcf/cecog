"""
datafiles.py - collect resources for distutils setup
"""

__author__ = 'rudolf.hoefler@gmail.com'
__copyright__ = ('The CellCognition Project'
                 'Copyright (c) 2006 - 2012'
                 'Gerlich Lab, IMBA Vienna, Austria'
                 'see AUTHORS.txt for contributions')
__licence__ = 'LGPL'
__url__ = 'www.cellcognition.org'

__all__ = ['get_data_files']

import os
import glob
import matplotlib
from os.path import basename, join, abspath

TARGET_DIR = 'resources'
RESOURCE_DIR = 'resources'

_rfiles = ['graph_template.txt', 'hmm.R', 'hmm_report.R', 'run_hmm.R']

# XXX special casing
if 'rsrc' in os.listdir(os.curdir):
    _rfiles = [join('rsrc', 'hmm', _rf) for _rf in _rfiles]
else:
    _rfiles = [join(os.pardir,
                    'rsrc', 'hmm', _rf) for _rf in _rfiles]


_rsc = ('config.ini', 'naming_schemas.ini', 'path_mappings.txt', 'font12.png')
_rsc = [join(abspath(RESOURCE_DIR), basename(rf)) for rf in _rsc]

_palettes = join(RESOURCE_DIR, 'palettes', 'zeiss')
_paltarget = join(TARGET_DIR, 'palettes', 'zeiss')
_battery_package = join(RESOURCE_DIR, 'battery_package')

def get_data_files(target_dir=TARGET_DIR, mpl_data=True):
    """Pack data files into list of (target-dir, list-of-files)-tuples"""

    dfiles = []
    if mpl_data:
        dfiles.extend(matplotlib.get_py2exe_datafiles())

    dfiles.append((target_dir, _rsc))
    dfiles.append((join(target_dir, 'rsrc', 'hmm'), _rfiles))
    dfiles.append((_paltarget, glob.glob(join(abspath(_palettes), '*.zip'))))

    for root, subdirs, files in os.walk(_battery_package):
        for file_ in files:
            if file_ not in (".git", ):
                target = root.replace(RESOURCE_DIR, TARGET_DIR)
                dfiles.append((target, [join(abspath(root), file_)]))
    return dfiles
