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

__all__ = ['OutputFrame']

#-------------------------------------------------------------------------------
# standard library imports:
#

#-------------------------------------------------------------------------------
# extension module imports:
#

#-------------------------------------------------------------------------------
# cecog imports:
#
from cecog.traits.analyzer.output import SECTION_NAME_OUTPUT
from cecog.gui.analyzer import BaseFrame

#-------------------------------------------------------------------------------
# constants:
#


#-------------------------------------------------------------------------------
# functions:
#


#-------------------------------------------------------------------------------
# classes:
#
class OutputFrame(BaseFrame):

    SECTION_NAME = SECTION_NAME_OUTPUT

    def __init__(self, settings, parent):
        super(OutputFrame, self).__init__(settings, parent)

        self.add_group(None,
                       [('rendering_labels_discwrite', (0,0,1,1)),
                        ('rendering_contours_discwrite', (1,0,1,1)),
                        ('rendering_contours_showids', (1,1,1,1)),
                        ('rendering_class_discwrite', (2,0,1,1)),
                        ('rendering_class_showids', (2,1,1,1)),
                        ('rendering_channel_gallery', (3,0,1,1)),
                        ], link='export_result_images',
                        label='Export result images')

        self.add_group(None,
                       [('export_object_counts', (0,0,1,1)),
                        ('export_object_details', (1,0,1,1)),
                        ('export_object_counts_ylim_max', (1,1,1,1)),
                        ('export_file_names', (2,0,1,1)),
                        ('export_tracking_as_dot', (3,0,1,1)),
                        ('export_track_data', (4,0,1,1)),
                        ], link='statistics', label='Statistics')

        self.add_group(None,
                       [('events_export_all_features', (0,0,1,1)),
                        ('events_export_gallery_images', (1,0,1,1)),
                        ('events_gallery_image_size', (1,1,1,1)),
                        ], link='events', label='Events')

        self.add_group('hdf5_create_file',
                       [('hdf5_include_raw_images', (0,0,1,1)),
                        ('hdf5_include_label_images', (1,0,1,1)),
                        ('hdf5_include_crack', (3,0,1,1)),
                        ('hdf5_include_features', (4,0,1,1)),
                        ('hdf5_include_classification', (5,0,1,1)),
                        ('hdf5_include_tracking', (6,0,1,1)),
                        ('hdf5_include_events', (7,0,1,1)),
                        (None, (8,0,1,3)),
                        ('hdf5_compression', (9,0,1,1)),
                        ('hdf5_merge_positions', (10,0,1,1)),
                        ])
        self.add_group('hdf5_reuse', [])
        self.add_expanding_spacer()
