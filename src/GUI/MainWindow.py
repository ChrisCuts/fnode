# -*- coding: utf-8 -*-
'''
Created on 10.08.2015

@author: derChris
'''

### extern
from PySide import QtCore, QtGui

from pydispatch import dispatcher


### Project intern
import GUI.icons #@UnusedImport
from GUI.NodeEditor import NodeEditor


### SIGNALs
_UNDO_STATUS = 'UNDO_STATUS'
_REDO_STATUS = 'REDO_STATUS'
_SAVED_STATUS = 'SAVED_STATUS'

_FILE_LOADED = 'FILE_LOADED'

_SAVE_BEFORE_QUIT = 'SAVE_BEFORE_QUIT?'

_MATLAB_ENGINE_STARTET = 'MATLAB_ENGINE_STARTET'

_style_sheet = '''
QTreeView, QGraphicsView, QLineEdit {Background: #FCFCFC}

QToolBar {background: qlineargradient( x1:0 y1:0, x2:0 y2:0.6, stop:0 #C0C0C0, stop:1 #A0A0A0); border: 1px solid #707070}

QMenuBar {background: #D0D0D0;}
QMenuBar::item {background: transparent;}
QMenuBar::item:selected {background: #80A0F0;}

SideBar {background: transparent;}
SideBarTree {background: transparent;}
'''


        
##################
### SIDEBARS
##################
class BuiltInSideBar(QtGui.QDockWidget):
    
    class SideBarTree(QtGui.QTreeView):
        
        def __init__(self, system = None, parent = None):
            
            super().__init__(parent)
            
            model = QtGui.QStandardItemModel()
            model.setSupportedDragActions(QtCore.Qt.CopyAction)
            self._rootItem = model.invisibleRootItem()
            
            self.build_list(self._rootItem, system.file_manager().root_folder())
            self.setModel(model)
            
            self.setDragEnabled(True)
            self.setDragDropMode(self.DragOnly)
            
            
            ### appearance
            self.setHeaderHidden(True)
            #self.setStyleSheet('QTreeView {background: #90000000; border : none}')
            
            #self.expanded.connect(self._item_expanded)
            
            
        def build_list(self, parent_item, folder):
            
            ### Function Selection
            item = QtGui.QStandardItem('Function Selection')
            item.setDragEnabled(True)
            item.setEditable(False)
            
            fileinfo = {'name': 'Function Selection',
                       'type': 'FunctionSelectionNode'}
            
            item.setData(fileinfo)
            parent_item.appendRow(item)
        
            ### Mat File
            item = QtGui.QStandardItem('Mat File')
            item.setDragEnabled(True)
            item.setEditable(False)
            
            fileinfo = {'name': 'Mat File',
                       'type': 'matFileNode'}
            
            item.setData(fileinfo)
            parent_item.appendRow(item)
        
     
        
        
    def __init__(self, title = '', nodeeditor = None, system= None, parent = None):
        
        super().__init__(title, parent)
        
        
        self.setWidget(self.SideBarTree(system))
        
        
        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        
        
        
class FunctionSideBar(QtGui.QDockWidget):
    
    class SideBarTree(QtGui.QTreeView):
        
        def __init__(self, system = None, parent = None):
            
            super().__init__(parent)
            
            model = QtGui.QStandardItemModel()
            model.setSupportedDragActions(QtCore.Qt.CopyAction)
            self._rootItem = model.invisibleRootItem()
            
            self.build_tree(self._rootItem, system.file_manager().root_folder())
            self.setModel(model)
            
            self.setDragEnabled(True)
            self.setDragDropMode(self.DragOnly)
            
            
            ### appearance
            self.setHeaderHidden(True)
            #self.setStyleSheet('QTreeView {background: #90000000; border : none}')
            
            self.expanded.connect(self._item_expanded)
            
            
        def build_tree(self, parent_item, folder):
            
            for subfolder in folder.subfolders():
                item = QtGui.QStandardItem(subfolder.name())
                item.setSelectable(False)
                item.setEditable(False)
                item.setDragEnabled(False)
                
                item.setData(subfolder)
                parent_item.appendRow(item)
                self.build_tree(item, subfolder)
                
            
            for filename, fileinfo in folder.files().items():
                
                item = QtGui.QStandardItem(filename)
                item.setDragEnabled(True)
                item.setEditable(False)
                
                item.setData(fileinfo)
                
                parent_item.appendRow(item)
            
        def _item_expanded(self, index):
            
            item = index.model().itemFromIndex(index)
            folder = item.data()
            folder.scan_folders()
            
            item.removeRows(0, item.rowCount())
            self.build_tree(item, folder)
     
        
        
    def __init__(self, title = '', nodeeditor = None, system= None, parent = None):
        
        super().__init__(title, parent)
        
        
        ### CurrentFolderWidget
        select_CF_dialog = QtGui.QFileDialog(self, 'Select workpath', system.file_manager().current_workpath())
        select_CF_dialog.setFileMode(select_CF_dialog.Directory)
        select_CF_dialog.fileSelected.connect(system.change_current_workpath)
        
        CFW_Layout = QtGui.QHBoxLayout()
        CFW_Layout.setContentsMargins(1, 0, 0, 0)
        
        CFW_Layout.addWidget(QtGui.QLineEdit(system.file_manager().current_workpath()))
        
        change_folder_button = QtGui.QPushButton()
        change_folder_button.setIcon(change_folder_button.style().standardIcon(QtGui.QStyle.SP_DirOpenIcon))
        CFW_Layout.addWidget(change_folder_button)
        change_folder_button.clicked.connect(select_CF_dialog.show)
        
        CurrentFolderWidget = QtGui.QWidget()
        CurrentFolderWidget.setLayout(CFW_Layout)
        
        ### SideBarLayout
        SideBarLayout = QtGui.QVBoxLayout()
        SideBarLayout.setContentsMargins(3, 0, 0, 0)
        
        SideBarLayout.addWidget(CurrentFolderWidget)
        SideBarLayout.addWidget(self.SideBarTree(system))
        
        SideBarWidget = QtGui.QWidget()
        SideBarWidget.setLayout(SideBarLayout)
        self.setWidget(SideBarWidget)
        
        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        #self.setStyleSheet('QDockWidget {background: #90000000}')
            
#         fx = QtGui.QGraphicsBlurEffect()
#         fx.setBlurRadius(5)
#         pixmap = QtGui.QPixmap(self.size())
#         pixmap = pixmap.grabWidget(nodeeditor)
#         
#         self._blur = QtGui.QLabel(self)
#         self._blur.setGeometry(self.geometry())
#         self._blur.setPixmap(pixmap)
#         self._blur.setGraphicsEffect(fx)
#         self._blur.setText('hy')
#         self._nodeeditor = nodeeditor
#         
        

        
        
##################
### MAINWINDOW
##################  
class MainWindow(QtGui.QMainWindow):
    
    def __init__(self, parent = None, system = None):
        
        super(MainWindow, self).__init__(parent)
        
        self._system = system
        
        self.setGeometry(100 ,100, 1000, 600)
        
        self._window_title = 'fNode Environment'
        self._update_title()
        
        self.setStyleSheet(_style_sheet)
        
        #self.setCentralWidget(QtGui.QWidget())
        self._nodeeditor = NodeEditor(self, system = system)
        self._nodeeditor.setGeometry(0, 0, self.width(), self.height())
        self.setCentralWidget(self._nodeeditor)
        
        functionsidebar = FunctionSideBar(' Function Browser', self._nodeeditor, system)
        builtinsidebar = BuiltInSideBar(' Built In Nodes', self._nodeeditor, system)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, functionsidebar)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, builtinsidebar)
        
        
        #############
        ### MENU BAR
        #############
        menu = QtGui.QMenuBar()
        
        ### FILE
        menu_file = menu.addMenu('File')
        menu_file.addAction('New').triggered.connect(system.clear)
        
        menu_file_open = menu_file.addAction('Open')
        menu_file_open.triggered.connect(system.load)
        
        menu_file.addSeparator()
        
        menu_file_save = menu_file.addAction('Save')
        menu_file_save.triggered.connect(system.save)
        menu_file_save.setShortcut(QtGui.QKeySequence.Save)
        
        menu_file_save_as = menu_file.addAction('Save As')
        #menu_file_save_as.triggered.connect()
        menu_file_save_as.setShortcut(QtGui.QKeySequence.SaveAs)
        menu_file.addSeparator()
        menu_file.addAction('Exit').triggered.connect(system.quit)
        
        ### EDIT
        menu_edit = menu.addMenu('Edit')
        
        self._menu_edit_undo = menu_edit.addAction('Undo')
        self._menu_edit_undo.setEnabled(False)
        self._menu_edit_undo.triggered.connect(system.undo)
        self._menu_edit_undo.setShortcut(QtGui.QKeySequence.Undo)
        self._menu_edit_undo_enable = lambda status: self._menu_edit_undo.setEnabled(status)
        dispatcher.connect(self._menu_edit_undo_enable, signal=_UNDO_STATUS, sender=system)
        
        self._menu_edit_redo = menu_edit.addAction('Redo')
        self._menu_edit_redo.setEnabled(False)
        self._menu_edit_redo.triggered.connect(system.redo)
        self._menu_edit_redo.setShortcut(QtGui.QKeySequence.Redo)
        self._menu_edit_redo_enable = lambda status: self._menu_edit_redo.setEnabled(status)
        dispatcher.connect(self._menu_edit_redo_enable, signal=_REDO_STATUS, sender=system)
        
        menu_edit.addSeparator()
        
        menu_edit_cut = menu_edit.addAction('Cut')
        menu_edit_cut.triggered.connect(lambda : system.cut(self._nodeeditor.scene().selectedNodes()))
        menu_edit_cut.setShortcut(QtGui.QKeySequence.Cut)
        
        menu_edit_copy = menu_edit.addAction('Copy')
        menu_edit_copy.triggered.connect(lambda : system.copy(self._nodeeditor.scene().selectedNodes()))
        menu_edit_copy.setShortcut(QtGui.QKeySequence.Copy)
        
        menu_edit_paste = menu_edit.addAction('Paste')
        menu_edit_paste.triggered.connect(system.paste)
        menu_edit_paste.setShortcut(QtGui.QKeySequence.Paste)
        
        ### RUN
        menu_run = menu.addMenu('Run')
        menu_run_run = menu_run.addAction('Run System')
        menu_run_run.triggered.connect(system.run)
        menu_run_run.setShortcut(QtGui.QKeySequence('CTRL+R'))
        
        ### WINDOW
        menu_window = menu.addMenu('Window')
        menu_window.addAction(functionsidebar.toggleViewAction())
        menu_window.addAction('Preferences')
        
        self.setMenuBar(menu)
        
        ##############
        ### TOOLBAR
        ##############
        toolbar = QtGui.QToolBar(self)
        toolbar.setMovable(False)
        
        
        toolbar.addAction(QtGui.QIcon(':/toolbar/new.svg'), 'New').triggered.connect(system.clear)
        toolbar.addAction(QtGui.QIcon(':/toolbar/open.svg'), 'Open')
        
        tb_save = toolbar.addAction(QtGui.QIcon(':/toolbar/save.svg'), 'Save')
        tb_save.setEnabled(False)
        tb_save.triggered.connect(system.save)
        self._tb_save_enable = lambda status: tb_save.setEnabled(not status)
        dispatcher.connect(self._tb_save_enable, signal= _SAVED_STATUS, sender= system)
        
        toolbar.addSeparator()
        
        tb_undo = toolbar.addAction(QtGui.QIcon(':/toolbar/undo.svg'), 'Undo')
        tb_undo.setEnabled(False)
        tb_undo.triggered.connect(system.undo)
        self._tb_undo_enable = lambda status: tb_undo.setEnabled(status)
        dispatcher.connect(self._tb_undo_enable, signal=_UNDO_STATUS, sender=system)
        
        tb_redo = toolbar.addAction(QtGui.QIcon(':/toolbar/redo.svg'), 'Redo')
        tb_redo.setEnabled(False)
        tb_redo.triggered.connect(system.redo)
        self._tb_redo_enable = lambda status: tb_redo.setEnabled(status)
        dispatcher.connect(self._tb_redo_enable, signal=_REDO_STATUS, sender=system)
        
        toolbar.addAction(QtGui.QIcon(':/toolbar/cut.svg'), 'Cut')
        toolbar.addAction(QtGui.QIcon(':/toolbar/copy.svg'), 'Copy')
        toolbar.addAction(QtGui.QIcon(':/toolbar/paste.svg'), 'Paste')
        
        toolbar.addSeparator()
        
        tb_run = toolbar.addAction(QtGui.QIcon(':/toolbar/run.svg'), 'Run')
        tb_run.triggered.connect(system.run)
        
        self.addToolBar(toolbar)
         
#         blur = QtGui.QLabel(self)
#         fx = QtGui.QGraphicsBlurEffect()
#         fx.setBlurRadius(5)
#         
#         blur.setFixedHeight(self.height())
#         blur.setFixedWidth(self.width())
#         
#         blur.setPixmap(self.grab())
#         blur.setGraphicsEffect(fx)
    
        ### EVENT HANDLING
        dispatcher.connect(self._update_title, signal= _SAVED_STATUS, sender= system)
        dispatcher.connect(self._update_title, signal= _FILE_LOADED, sender= system)

        
    def system(self):
        
        return self._system
    
    def saved_status_changed(self, status):
        
        if not status and not self.windowTitle().endswith('*'):
            self.setWindowTitle(self.windowTitle() + '*')
        elif status and self.windowTitle().endswith('*'):
            self.setWindowTitle(self.windowTitle()[:-1])

    def _update_title(self):
        
        title = self._window_title
        
        if self._system.filename():
            title += ' - ' + self._system.filename()
        
        if not self._system.saved():
            title += '*'
            
        self.setWindowTitle(title)
                            
    def cleanup(self):
        
        for item in self._nodeeditor.scene().items():
            
            del(item)

    def closeEvent(self, event):
    
        self._system.quit()
        
class MyApp(QtGui.QApplication):

    def notify(self, receiver, event):
        
        try:
            return super().notify(receiver, event)
        except:
            
            import traceback
            traceback.print_exc()
            
class GUI():
    
    def __init__(self, system= None):
        
        self._system = system
        
        self._main = MainWindow(system = system)
        
        icon = QtGui.QIcon(':/icon.svg')
        self._main.setWindowIcon(icon)
        
        
        dispatcher.connect(self._save_before_quit_dialog, _SAVE_BEFORE_QUIT, sender= system)
    
    def start(self):
        
        self._main.show()
    
    def _save_before_quit_dialog(self):
        
#         box = QtGui.QMessageBox()
#         box.setText('There are unsaved changes. Do you want to save them?')
#         box.setIcon(box.Warning)
#         
#         box.addButton('Save', box.YesRole)
#         box.addButton('Save As', box.ApplyRole)
#         box.addButton('No', box.NoRole)
#         box.exec_()

  
        #TODO: ...
        pass
          
        
    def quit(self):
        
        self._main.cleanup()
        self._main.close()
        
    
    
        
if __name__ == '__main__':
    
    
    gui = GUI()
    gui.show()

    