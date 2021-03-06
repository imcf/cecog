"""
                           The CellCognition Project
        Copyright (c) 2006 - 2012 Michael Held, Christoph Sommer
                      Gerlich Lab, ETH Zurich, Switzerland
                              www.cellcognition.org

              CellCognition is distributed under the LGPL License.
                        See trunk/LICENSE.txt for details.
                 See trunk/AUTHORS.txt for author contributions.
"""

__author__ = 'Michael Held'
__date__ = '$Date$'
__revision__ = '$Rev$'
__source__ = '$URL$'

__all__ = []

#-------------------------------------------------------------------------------
# standard library imports:
#

#-------------------------------------------------------------------------------
# extension module imports:
#

#-------------------------------------------------------------------------------
# cecog imports:
#

#-------------------------------------------------------------------------------
# constants:
#
CONTROL_1 = 'CONTROL_1'
CONTROL_2 = 'CONTROL_2'

FEATURE_CATEGORIES = ['roisize',
                      'circularity',
                      'irregularity',
                      'irregularity2',
                      'axes',
                      'normbase',
                      'normbase2',
                      'levelset',
                      'convexhull',
                      'dynamics',
                      'granulometry',
                      'distance',
                      'moments',
                      ]

ZSLICE_PROJECTION_METHODS = ['maximum', 'average']

COMPRESSION_FORMATS = ['raw', 'bz2', 'gz']
TRACKING_METHODS = ['ClassificationCellTracker',]
TRACKING_DURATION_UNIT_FRAMES = 'frames'
TRACKING_DURATION_UNIT_MINUTES = 'minutes'
TRACKING_DURATION_UNIT_SECONDS = 'seconds'
TRACKING_DURATION_UNITS_DEFAULT = [TRACKING_DURATION_UNIT_FRAMES,
                                   ]
TRACKING_DURATION_UNITS_TIMELAPSE = [TRACKING_DURATION_UNIT_FRAMES,
                                     TRACKING_DURATION_UNIT_MINUTES,
                                     TRACKING_DURATION_UNIT_SECONDS,
                                     ]

R_LIBRARIES = ['hwriter', 'RColorBrewer', 'igraph']
