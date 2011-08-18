"""
                           The CellCognition Project
                     Copyright (c) 2006 - 2011 Michael Held
                      Gerlich Lab, ETH Zurich, Switzerland
                              www.cellcognition.org

              CellCognition is distributed under the LGPL License.
                        See trunk/LICENSE.txt for details.
                 See trunk/AUTHORS.txt for author contributions.
"""
__all__ = []

#-------------------------------------------------------------------------------
# standard library imports:
#
from PyQt4 import QtGui, QtCore
import zlib
import base64

#-------------------------------------------------------------------------------
# extension module imports:
#
import random
import getopt
import qimage2ndarray
import sys
import numpy
import time as timing

#-------------------------------------------------------------------------------
# cecog imports:
#
from cecog.gui.imageviewer import HoverPolygonItem
from cecog.io.dataprovider import File
from cecog.io.dataprovider import trajectory_features, TerminalObjectItem, ObjectItem
from pdk.datetimeutils import StopWatch



#-------------------------------------------------------------------------------
# constants:
#


#-------------------------------------------------------------------------------
# functions:
#
import types
def MixIn(pyClass, mixInClass, makeAncestor=0):
    if makeAncestor:
        if mixInClass not in pyClass.__bases__:
            pyClass.__bases__ = pyClass.__bases__ + (mixInClass,)
    else:
        # Recursively traverse the mix-in ancestor
        # classes in order to support inheritance
        baseClasses = list(mixInClass.__bases__)
        baseClasses.reverse()
        for baseClass in baseClasses:
            MixIn(pyClass, baseClass)
        # Install the mix-in methods into the class
        for name in dir(mixInClass):
            if not name.startswith('__'):
            # skip private members
                member = getattr(mixInClass, name)
                if type(member) is types.MethodType:
                    member = member.im_func
                setattr(pyClass, name, member)


class MainWindow(QtGui.QMainWindow):
    def __init__(self, filename=None, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setStyleSheet('background-color: qlineargradient(x1: 0, y1: 0, x2: 500, y2: 500, stop: 0 #444444, stop: 1 #0A0A0A);') 
        self.setGeometry(100,100,1200,800)
        self.setWindowTitle('tracklet browser')
        
        self.mnu_open = QtGui.QAction('&Open', self)
        self.mnu_open.triggered.connect(self.open_file)
        
        self.mnu_change_view = QtGui.QAction('&Change gallery size', self)
        self.mnu_change_view.triggered.connect(self.change_gallery_size)
        
        file_menu = self.menuBar().addMenu('&File')
        view_menu = self.menuBar().addMenu('&View')
        file_menu.addAction(self.mnu_open)
        view_menu.addAction(self.mnu_change_view)

        
        self.tracklet_widget = TrackletBrowser(self)
        self.setCentralWidget(self.tracklet_widget)  
        
        if filename is not None:
            self.tracklet_widget.open_file(filename)
            
            
            
    def closeEvent(self, cevent):
        try:
            if self.tracklet_widget.data_provider is not None:
                self.tracklet_widget.data_provider.close()
                print 'Closing hdf5 file'
        except:
            print 'Could not close file or no file has been open'
        finally:
            cevent.accept()
        
    def change_gallery_size(self):
        val, ok = QtGui.QInputDialog.getInt(self, 'New gallery image size', 'Size', 
                                            value=CellTerminalObjectItemMixin.BOUNDING_BOX_SIZE, 
                                            min=10, 
                                            max=1000)
        if ok:
            CellTerminalObjectItemMixin.BOUNDING_BOX_SIZE = val
            self.tracklet_widget.data_provider.clearObjectItemCache()
                    
            self.tracklet_widget.show_position(self.tracklet_widget._current_position_key)
        
    def open_file(self):
        filename = str(QtGui.QFileDialog.getOpenFileName(self, 'Open hdf5 file', '.', 'hdf5 files (*.h5  *.hdf5)'))  
        if filename:                                              
            self.tracklet_widget.open_file(filename)
        
class ZoomedQGraphicsView(QtGui.QGraphicsView):  
    def wheelEvent(self, event):
        keys = QtGui.QApplication.keyboardModifiers()
        k_ctrl = (keys == QtCore.Qt.ControlModifier)

        self.mousePos = self.mapToScene(event.pos())
        grviewCenter  = self.mapToScene(self.viewport().rect().center())

        if k_ctrl is True:
            if event.delta() > 0:
                scaleFactor = 1.1
            else:
                scaleFactor = 0.9
            self.scale(scaleFactor, scaleFactor)
            
            mousePosAfterScale = self.mapToScene(event.pos())
            offset = self.mousePos - mousePosAfterScale
            newGrviewCenter = grviewCenter + offset
            self.centerOn(newGrviewCenter)
            
class PositionThumbnail(QtGui.QLabel):
    item_length = 10
    item_height = 2
    css = 'background-color: transparent;'
    
    def __init__(self, position_key, position, parent=None):
        QtGui.QLabel.__init__(self, parent)
        self.parent = parent
        events = position.get_objects('event')
        self.position_key = position_key
        thumbnail_pixmap = QtGui.QPixmap(20*self.item_length, len(events)*self.item_height)
        thumbnail_pixmap.fill(QtCore.Qt.black)
        painter = QtGui.QPainter()
        painter.begin(thumbnail_pixmap)
        for r, event in enumerate(events):
            for c, pp in enumerate(event.children()):
                line_pen = QtGui.QPen(QtGui.QColor(pp.class_color))
                line_pen.setWidth(3)
                painter.setPen(line_pen)
                painter.drawLine(c*self.item_length, r*self.item_height, 
                                 (c+1)*self.item_length, r*self.item_height)
        painter.end()
            
        self.height = thumbnail_pixmap.height()
        self.setPixmap(thumbnail_pixmap)
        self.setStyleSheet(self.css)
        self.setToolTip('Sample %s\nPlate %s \nExperiment %s\nPosition %s' % position_key)
        self.setMinimumHeight(self.height)
    
    def mouseDoubleClickEvent(self, *args, **kwargs):
        QtGui.QLabel.mouseDoubleClickEvent(self, *args, **kwargs)
        self.parent.clicked.emit(self.position_key)
        
    
            
class TrackletThumbnailList(QtGui.QWidget):
    css = '''background-color: transparent; 
             color: white; 
             font: bold 12px;
             min-width: 10em; 
          '''
    clicked = QtCore.pyqtSignal(tuple)
    
    def __init__(self, data_provider, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.main_layout = QtGui.QHBoxLayout()
        
        
        for position_key in data_provider.positions:
            tn_position = PositionThumbnail(position_key, data_provider[position_key], self)
            tn_widget = QtGui.QWidget(self)
            tn_layout = QtGui.QVBoxLayout()
            tn_layout.addWidget(QtGui.QLabel('%s %s' % (position_key[1], position_key[3])))
            tn_layout.addWidget(tn_position)
            tn_widget.setLayout(tn_layout)
            self.main_layout.addWidget(tn_widget)
            
        self.main_layout.addStretch()
        self.setLayout(self.main_layout)
        self.setMinimumHeight(tn_position.height + 20)

        self.setStyleSheet(self.css)
        
    def paintEvent(self, event):
        opt = QtGui.QStyleOption();
        opt.init(self);
        p = QtGui.QPainter(self);
        self.style().drawPrimitive(QtGui.QStyle.PE_Widget, opt, p, self)

class TrackletBrowser(QtGui.QWidget):
    css = '''QPushButton, QComboBox {background-color: transparent;
                             border-style: outset;
                             border-width: 2px;
                             border-radius: 4px;
                             border-color: white;
                             color: white;
                             font: bold 14px;
                             min-width: 10em;
                             padding: 2px;}
                QPushButton :pressed {
                             background-color: rgb(50, 50, 50);
                             border-style: inset;}
                 QScrollBar:horizontal {
                     border: 2px solid grey;
                     background: black;
                 }

            
                     '''
    
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.data_provider = None
        self.scene = QtGui.QGraphicsScene()
        self.scene.setBackgroundBrush(QtGui.QBrush(QtCore.Qt.black))
        
        self.view = ZoomedQGraphicsView(self.scene)
        self.view.setMouseTracking(True)
        
        self.view.setStyleSheet(self.css)
        
        self.main_layout = QtGui.QVBoxLayout()
        self.setLayout(self.main_layout)
 
        self.main_layout.addWidget(self.view)
        
        self.view_hud_layout = QtGui.QHBoxLayout(self.view)
        self.view_hud_btn_layout = QtGui.QVBoxLayout()
        self.view_hud_layout.addLayout(self.view_hud_btn_layout)
        
        self.btn_sort_randomly = QtGui.QPushButton('Sort random')
        self.btn_sort_randomly.clicked.connect(self.sortRandomly)
        self.view_hud_btn_layout.addWidget(self.btn_sort_randomly)
        
        self.btns_sort = []
        
        for tf in trajectory_features:
            temp = QtGui.QPushButton(tf.name)
            temp.clicked.connect(lambda state, x=tf.name: self.sortTracksByFeature(x))
            self.btns_sort.append(temp)
            self.view_hud_btn_layout.addWidget(temp)
            
        self.btn_toggle_contours = QtGui.QPushButton('Toggle contours')
        self.btn_toggle_contours.setCheckable(True)
        self.btn_toggle_contours.setChecked(True)

        self.view_hud_btn_layout.addWidget(self.btn_toggle_contours)
        
        self.btn_selectTen = QtGui.QPushButton('Select 10')
        self.btn_selectTen.clicked.connect(self.selectTenRandomTrajectories)
        self.view_hud_btn_layout.addWidget(self.btn_selectTen)
        
        self.btn_selectAll = QtGui.QPushButton('Select All')
        self.btn_selectAll.clicked.connect(self.selectAll)
        self.view_hud_btn_layout.addWidget(self.btn_selectAll)
        
        self.btn_selectTransition = QtGui.QPushButton('Select Transition 0,1')
        self.btn_selectTransition.clicked.connect(self.selectTransition)
        self.view_hud_btn_layout.addWidget(self.btn_selectTransition)
        
        self.btn_toggleBars = QtGui.QPushButton('Toggle Bars')
        self.btn_toggleBars.setCheckable(True)
        self.btn_toggleBars.setChecked(True)
        self.btn_toggleBars.toggled.connect(self.showGalleryImage)
        self.view_hud_btn_layout.addWidget(self.btn_toggleBars)
        
        self.cmb_align = QtGui.QComboBox()
        self.cmb_align.addItems(['Left', 'Absolute time', 'Custom'])
        self.cmb_align.currentIndexChanged.connect(self.cb_change_vertical_alignment)        
        self.view_hud_btn_layout.addWidget(self.cmb_align)
        
        self.view_hud_btn_layout.addStretch()
        
        self.btn_toggle_contours.toggled.connect(self.showContours)
        
        self.view_hud_layout.addStretch()
        
        self.view.setDragMode(self.view.ScrollHandDrag)
        
        
        
    def show_position(self, position_key):
        tic = timing.time()
        self.scene.clear()
        self._current_position_key = position_key
        position = self.data_provider[position_key]
        
        self._root_items = []
        events = position.get_objects('event')
        
        for event in events.iter_random(500):
            g_event = event.GraphicsItemType(event)
            g_event.setHandlesChildEvents(False)
            self.scene.addItem(g_event)
            self._root_items.append(g_event)
        print '  Loading events took %5.2f' % (timing.time() - tic)
            
        self.GraphicsItemLayouter = event.GraphicsItemLayouter(self._root_items, self)
            
        self.update_()
        print '  Total Rendering of position took %5.2f' % (timing.time() - tic)
    
    def cb_change_vertical_alignment(self, index): 
        self.GraphicsItemLayouter._align_vertically = index
        self.update_()
           
    def open_file(self, filename):
        self.data_provider = File(filename)
        self.thumbnails = TrackletThumbnailList(self.data_provider, self)
        self.thumbnails.clicked.connect(self.show_position)
        self.main_layout.addWidget(self.thumbnails)
        
        
    def total_height(self):
        return sum([x.height for x in self._root_items])
    
    def update_(self):
        self.GraphicsItemLayouter()
        
        
    def showGalleryImage(self, state):
        for ti in self._root_items:
            ti.showGalleryImage(state)
        self.update_()
            
    def sortTracks(self):   
        for new_row, perm_idx in enumerate(self._permutation):
            self._root_items[perm_idx].moveToRow(new_row)
            
    def sortRandomly(self):
        random.shuffle(self._root_items)
        self.update_()
        
    def sortTracksByFeature(self, feature_name):
        self._root_items.sort(cmp=lambda x,y: cmp(x.object_item[feature_name],y.object_item[feature_name]))
        self.update_()
    
    def showContours(self, state):
        for ti in self._root_items:
            if ti.is_selected:
                ti.showContours(state)
        self.update_()
        
    def selectTenRandomTrajectories(self):
        for ti in self._root_items:
            ti.is_selected = True
        for r in random.sample(range(len(self._root_items)), len(self._root_items) - 10):
            self._root_items[r].is_selected = False
        self.update_()
        
    def selectAll(self):
        for ti in self._root_items:
            ti.is_selected = True
#            ti.moveToColumn(0)
#        self.GraphicsItemLayouter._align_vertically = self.cmb_align.setCurrentIndex(self.GraphicsItemLayouter.ALIGN_LEFT)
        self.update_()
        
    def selectTransition(self):
        for ti in self._root_items:
            ti.is_selected = False
            trans_pos = reduce(lambda x,y: str(x) + str(y), ti.object_item['prediction']).find('01')
            if trans_pos > 0:
                ti.is_selected = True
                ti.column = - (trans_pos + 1)
        self.GraphicsItemLayouter._align_vertically = self.cmb_align.setCurrentIndex(self.GraphicsItemLayouter.ALIGN_CUSTOM)
    
    def reset(self):
        for t in self._root_items:
            t.resetPos()
               
            
class GraphicsObjectItemBase(QtGui.QGraphicsItemGroup):
    def __init__(self, parent):
        QtGui.QGraphicsItemGroup.__init__(self, parent)
        self.is_selected = True
        
    def moveToRow(self, row):
        self.row = row
        self.setPos(self.column * self.width, row * self.height)
        
    def moveToColumn(self, col):
        self.column = col
        self.setPos(col * self.width, self.row * self.height)
      
        
    
class GraphicsObjectItem(GraphicsObjectItemBase):
    def __init__(self, object_item, parent=None):
        GraphicsObjectItemBase.__init__(self, parent)
        self.object_item = object_item
        
    
class EventGraphicsItem(GraphicsObjectItem):
    def __init__(self, object_item, parent=None):
        GraphicsObjectItem.__init__(self, object_item, parent)
    
        self.sub_items = []
        for col, sub_item in enumerate(object_item.children()):
            g_sub_item = sub_item.GraphicsItemType(sub_item, self)
            g_sub_item.moveToColumn(col)
            self.sub_items.append(g_sub_item)
            self.addToGroup(g_sub_item)
        self.row = object_item.id
        self.column = 0
        self.height = self.sub_items[0].height
    
    def showGalleryImage(self, state):
        for sub_item in self.sub_items:
            sub_item.showGalleryImage(state)
        self.height = self.sub_items[0].height
            
    def showContours(self, state):
        for sub_item in self.sub_items:
            sub_item.showContours(state)
            
    @property
    def width(self):
        return sum([x.width for x in self.sub_items])
        
             
class GraphicsTerminalObjectItem(GraphicsObjectItemBase):
    def __init__(self, object_item, parent=None):
        GraphicsObjectItemBase.__init__(self, parent=None)
        self.object_item = object_item
        
class CellGraphicsItem(GraphicsTerminalObjectItem):
    PREDICTION_BAR_HEIGHT = 4
    PREDICTION_BAR_X_PADDING = 0
    
    @property
    def width(self):
        return self.object_item.BOUNDING_BOX_SIZE
    
    def __init__(self, object_item, parent=None):
        GraphicsTerminalObjectItem.__init__(self, object_item, parent=None)
        gallery_item = QtGui.QGraphicsPixmapItem(QtGui.QPixmap(qimage2ndarray.array2qimage(object_item.image)))
        gallery_item.setPos(0, self.PREDICTION_BAR_HEIGHT)
        
        
        bar_item = QtGui.QGraphicsLineItem(self.PREDICTION_BAR_X_PADDING, 0, self.width - self.PREDICTION_BAR_X_PADDING, 0)
        bar_pen = QtGui.QPen(QtGui.QColor(object_item.class_color))
        bar_pen.setWidth(self.PREDICTION_BAR_HEIGHT)
        bar_item.setPen(bar_pen)
        
        contour_item = HoverPolygonItem(QtGui.QPolygonF(map(lambda x: QtCore.QPointF(x[0],x[1]), object_item.crack_contour.tolist())))
        contour_item.setPos(0, self.PREDICTION_BAR_HEIGHT)
        contour_item.setPen(QtGui.QPen(QtGui.QColor(object_item.class_color)))
        contour_item.setAcceptHoverEvents(True)
        
        self.addToGroup(gallery_item)
        self.addToGroup(bar_item)
        self.addToGroup(contour_item)
        
        self.bar_item = bar_item
        self.contour_item = contour_item
        self.gallery_item = gallery_item
        
        self.row = 0 
        self.column = object_item.time
        self.height = self.width + self.PREDICTION_BAR_HEIGHT 
        
    def showGalleryImage(self, state):
        self.contour_item.setVisible(state)
        self.gallery_item.setVisible(state)
        if state:
            self.height = self.width + self.PREDICTION_BAR_HEIGHT 
        else:
            self.height = self.PREDICTION_BAR_HEIGHT 
            
    def showContours(self, state):
        self.contour_item.setVisible(state)
        
class GraphicsLayouterBase(QtGui.QWidget):
    properties = {}
    def __init__(self, items, parent):
        QtGui.QWidget.__init__(self, parent)
        self._items = items     
    def __call__(self):
        'print default layouting'   

class EventGraphicsLayouter(GraphicsLayouterBase):
    properties = {'alignment': 0}
    ALIGN_LEFT = 0
    ALIGN_ABSOLUT_TIME = 1
    ALIGN_CUSTOM = 2
    
    def __init__(self, items, parent):
        GraphicsLayouterBase.__init__(self, items, parent)
        self._align_vertically = self.ALIGN_LEFT
        
    def __call__(self):
        row = 0
        for ti in self._items:
            if ti.is_selected:
                ti.moveToRow(row)
                row += 1
                ti.setVisible(True)
            else:
                ti.setVisible(False)
            if self._align_vertically == self.ALIGN_LEFT:
                ti.moveToColumn(0)
            elif self._align_vertically == self.ALIGN_ABSOLUT_TIME:
                ti.moveToColumn(ti.sub_items[0].object_item.time)
            elif self._align_vertically == self.ALIGN_CUSTOM:
                ti.moveToColumn(ti.column)
        
class CellGraphicsLayouter(GraphicsLayouterBase):
    def __init__(self, items, parent):
        GraphicsLayouterBase.__init__(self, items, parent)
    
    def __call__(self):
        row = 0
        col = 0
        for ti in self._items:
            if ti.is_selected:
                ti.moveToRow(row)
                ti.moveToColumn(col)
                ti.setVisible(True)
                col += 1
            else:
                ti.setVisible(False)
            
            if col > 26:
                row += 1
                col = 0
        
        
class CellTerminalObjectItemMixin():
    GraphicsItemType = CellGraphicsItem
    GraphicsItemLayouter = CellGraphicsLayouter
    BOUNDING_BOX_SIZE = 100
    
    @property
    def image(self):
        if not hasattr(self, '_image'):
            channel_idx = self.channel_idx
            image_own = self._get_image(self.time, self.local_idx, channel_idx)
            
            #sib = self.get_siblings()
            if False:#sib is not None:
                image_sib = sib.image
                new_shape = (self.width,)*2 + (3,)
                image = numpy.zeros(new_shape, dtype=numpy.uint8)
                image[0:image_own.shape[0],0:image_own.shape[1],0] = image_own
                image[0:image_sib.shape[0],0:image_sib.shape[1],1] = image_sib
            else:
                image = image_own
            self._image = image
        
        return self._image 
    
    @property
    def crack_contour(self):
        crack_contour = self._get_crack_contours(self.time, self.local_idx)
        bb = self.bounding_box
        crack_contour[:,0] -= bb[0][0]
        crack_contour[:,1] -= bb[0][1]  
        return crack_contour.clip(0, self.BOUNDING_BOX_SIZE)
    
    @property
    def predicted_class(self):
        # TODO: This can access can be cached by parent
        if not hasattr(self, '_predicted_class'):
            classifier_idx = self.classifier_idx()
            self._predicted_class = self._get_additional_object_data(self.name, 'classifier', classifier_idx) \
                                        ['prediction'][self.idx]
        return self._predicted_class[0]
    
    @property
    def time(self):
        return self._local_idx[0]
    
    @property
    def local_idx(self):
        return self._local_idx[1]
    
    def classifier_idx(self):
        return self.get_position.object_classifier_index[self.name]
    
    @property
    def channel_idx(self):
        if not hasattr(self, '_channel_idx'):
            self._channel_idx = self.get_position.regions[self.get_position.sub_objects[self.name]]['channel_idx']
        return self._channel_idx
        
    @property
    def bounding_box(self):
        if not hasattr(self, '_bounding_box'):   
            objects = self.parent.object_np_cache['terminals'][self.time]['object']
            self._bounding_box = (objects['upper_left'][self.local_idx], objects['lower_right'][self.local_idx])
        return self._bounding_box
    
    def _get_image(self, t, obj_idx, c, bounding_box=None):
        if bounding_box is None:
            ul, lr = self.bounding_box
        else:
            ul, lr = bounding_box
        offset_0 = (self.BOUNDING_BOX_SIZE - lr[0] + ul[0])
        offset_1 = (self.BOUNDING_BOX_SIZE - lr[1] + ul[1]) 
        ul[0] = max(0, ul[0] - offset_0/2 - cmp(offset_0%2,0) * offset_0 % 2) 
        ul[1] = max(0, ul[1] - offset_1/2 - cmp(offset_1%2,0) * offset_1 % 2)      
        lr[0] = min(self.get_position._hf_group_np_copy.shape[4], lr[0] + offset_0/2) 
        lr[1] = min(self.get_position._hf_group_np_copy.shape[3], lr[1] + offset_1/2) 
        
        self._bounding_box = (ul, lr)
        # TODO: get_iamge returns am image which might have a smaller shape than 
        #       the requested BOUNDING_BOX_SIZE, I dont see a chance to really
        #       fix it, without doing a copy...
        res = self.get_position._hf_group_np_copy[c, t, 0, ul[1]:lr[1], ul[0]:lr[0]]
        return res

    def _get_crack_contours(self, t, obj_idx):  
        crack_contours_string = self.parent.object_np_cache['terminals'][t]['crack_contours'][obj_idx]                               
        return numpy.asarray(zlib.decompress( \
                             base64.b64decode(crack_contours_string)).split(','), \
                             dtype=numpy.float32).reshape(-1,2)
        
    def _get_object_data(self, t, obj_idx, c):
        bb = self.get_bounding_box(t, obj_idx, c)
        img, new_bb = self.get_image(t, obj_idx, c, bb)
        cc = self.get_crack_contours(t, obj_idx, c)
        cc[:,0] -= new_bb[0][0]
        cc[:,1] -= new_bb[0][1]
        return img, cc
    
    def _get_additional_object_data(self, object_name, data_fied_name, index):
        return self.get_position._hf_group['object'][object_name][data_fied_name][str(index)]
    
    @property
    def class_color(self):
        if not hasattr(self, '_class_color'):
            classifier = self.get_position.object_classifier[self.name, self.get_position.object_classifier_index[self.name]]
            self._class_color = dict(enumerate(classifier['schema']['color'].tolist()))       
        return self._class_color[self.predicted_class]
    
    def compute_features(self):
#        print 'compute feature call for', self.name, self.id  
        pass
    

class EventObjectItemMixin():
    GraphicsItemType = EventGraphicsItem
    GraphicsItemLayouter = EventGraphicsLayouter
    def compute_features(self):
#        print 'compute feature call for', self.name, self.id  
        for feature in trajectory_features:
            if isinstance(self, feature.type):
                self[feature.name] =  feature.compute(self.children())
                
        self['prediction'] = [x.predicted_class for x in self.children()]
        
MixIn(TerminalObjectItem, CellTerminalObjectItemMixin, True)
MixIn(ObjectItem, EventObjectItemMixin, True)

        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv) 
    file, _ = getopt.getopt(sys.argv[1:], 'f:')
    if len(file) == 1:
        file = file[0][1]
    else:
        file = None
        
    mainwindow = MainWindow(file)
    
#    import cProfile, pstats
#    cProfile.run('mainwindow = MainWindow(file)', 'profile-result')
#    ps = pstats.Stats('profile-result')
#    ps.strip_dirs().sort_stats('cumulative').print_stats()
    
    mainwindow.show()
    app.exec_()
    


