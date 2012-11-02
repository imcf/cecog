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

__all__ = ['SectionTracking']

#-------------------------------------------------------------------------------
# standard library imports:
#

#-------------------------------------------------------------------------------
# extension module imports:
#

#-------------------------------------------------------------------------------
# cecog imports:
#
from cecog.traits.config import _Section
from cecog.gui.guitraits import (IntTrait,
                                 BooleanTrait,
                                 SelectionTrait,
                                 )
from cecog.analyzer import COMPRESSION_FORMATS

#-------------------------------------------------------------------------------
# constants:
#
SECTION_NAME_TRACKING = 'Tracking'

#-------------------------------------------------------------------------------
# functions:
#


#-------------------------------------------------------------------------------
# classes:
#
class SectionTracking(_Section):

    SECTION_NAME = SECTION_NAME_TRACKING

    OPTIONS = [
      ('tracking',
       [('tracking_maxobjectdistance',
            IntTrait(0, 0, 4000, label='Max object x-y distance')),
        ('tracking_maxtrackinggap',
            IntTrait(0, 0, 4000, label='Max time-point gap')),
        ('tracking_maxsplitobjects',
            IntTrait(0, 0, 4000, label='Max split events')),
        ('tracking_maxindegree',
            IntTrait(1, 0, 4000, label='Max in-degree')),
        ('tracking_maxoutdegree',
            IntTrait(2, 0, 4000, label='Max out-degree')),
        ('tracking_exporttrackfeatures',
            BooleanTrait(True, label='Export tracks')),
        ('tracking_compressiontrackfeatures',
            SelectionTrait(COMPRESSION_FORMATS[0], COMPRESSION_FORMATS,
                           label='Compression')),
        ]),

      ('visualization',
       [('tracking_visualization',
            BooleanTrait(False, label='Visualization')),
        ('tracking_visualize_track_length',
            IntTrait(5, -1, 10000, label='Max. time-points')),
        ('tracking_centroid_radius',
            IntTrait(3, -1, 50, label='Centroid radius')),
        ]),
      ]
