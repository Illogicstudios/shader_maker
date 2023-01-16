import os
from functools import partial

# import maya.cmds as cmds
import maya.OpenMayaUI as omui

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

from shiboken2 import wrapInstance

from Shader import Shader, ShaderField

# CS mean create shaders part
# US mean update shaders part
class ShaderMaker(QtWidgets.QDialog):

    def __init__(self, parent=wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)):
        super(ShaderMaker, self).__init__(parent)

        # Model attributes
        self.__cs_folder_path = ""
        self.__us_folder_path = ""
        self.__cs_shaders = []

        # UI attributes
        self.__reinit_ui()

        # name the window
        self.setWindowTitle("Shader Maker")
        # make the window a "tool" in Maya's eyes so that it stays on top when you click off
        self.setWindowFlags(QtCore.Qt.Tool)
        # Makes the object get deleted from memory, not just hidden, when it is closed.
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # Create the layout, linking it to actions and refresh the display
        self.__create_ui()
        self.__refresh_btn()

    # Retrieve the selected object in maya
    def __retrieve_selected(self):
        # TODO
        pass

    # Reinitialize the ui in order to repopulate it
    def __reinit_ui(self):
        self.__ui_cs_folder_path = None
        self.__ui_us_folder_path = None
        self.__ui_cs_submit_btn = None
        self.__ui_us_submit_btn = None
        self.__ui_shaders_cs_lyt = None

    # Refresh the state of buttons
    def __refresh_btn(self):
        # TODO
        if self.__ui_cs_submit_btn is not None:
            self.__ui_cs_submit_btn.setEnabled(len(self.__cs_folder_path) > 0)
        if self.__ui_us_submit_btn is not None:
            self.__ui_us_submit_btn.setEnabled(len(self.__us_folder_path) > 0)

    def __browse_cs_folder(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Directory", "I:/battlestar_2206/assets\ch_panda/textures/02/panda_02_textures")
        if len(folder_path) > 0 and folder_path != self.__cs_folder_path:
            self.__ui_cs_folder_path.setText(folder_path)

    def __browse_us_folder(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Directory", "I:/battlestar_2206/assets\ch_panda/textures/02/panda_02_textures")
        if len(folder_path) > 0 and folder_path != self.__us_folder_path:
            self.__ui_us_folder_path.setText(folder_path)

    # Create the layout
    def __create_ui(self):
        # Reinit attributes of the UI
        self.__reinit_ui()
        width = 720
        height = 800
        self.setFixedSize(width, height)
        self.move(QtWidgets.QDesktopWidget().availableGeometry().center() - self.frameGeometry().center())

        # Some aesthetic value
        size_btn = QtCore.QSize(180, 30)
        icon_size = QtCore.QSize(18, 18)
        btn_icon_size = QtCore.QSize(24, 24)

        # Main Layout
        main_lyt = QtWidgets.QVBoxLayout()
        main_lyt.setContentsMargins(10, 15, 10, 10)
        main_lyt.setSpacing(20)
        self.setLayout(main_lyt)

        # Layout ML.1 : Create shaders
        cs_lyt = QtWidgets.QVBoxLayout()
        cs_lyt.setAlignment(QtCore.Qt.AlignTop)
        main_lyt.addLayout(cs_lyt)
        # Separator ML.1 | ML.2
        separator = QtWidgets.QFrame()
        separator.setMinimumWidth(1)
        separator.setFixedHeight(20)
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        separator.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        main_lyt.addWidget(separator)
        # Layout ML.2 : Update shaders
        us_lyt = QtWidgets.QVBoxLayout()
        us_lyt.setAlignment(QtCore.Qt.AlignTop)
        main_lyt.addLayout(us_lyt)

        # Layout ML.1.1 : Folder
        folder_cs_lyt = QtWidgets.QHBoxLayout()
        cs_lyt.addLayout(folder_cs_lyt)
        self.__ui_cs_folder_path = QtWidgets.QLineEdit()
        self.__ui_cs_folder_path.setFixedHeight(btn_icon_size.height() + 3)
        self.__ui_cs_folder_path.textChanged.connect(self.__on_folder_cs_changed)
        folder_cs_lyt.addWidget(self.__ui_cs_folder_path)
        browse_cs_btn = QtWidgets.QPushButton()
        browse_cs_btn.setIconSize(icon_size)
        browse_cs_btn.setFixedSize(btn_icon_size)
        browse_cs_btn.setIcon(QtGui.QIcon(
            QtGui.QPixmap("C:/Users/m.jenin/Documents/marius/shader_maker/assets/browse.png")))  # TODO CHANGE
        browse_cs_btn.clicked.connect(partial(self.__browse_cs_folder))
        folder_cs_lyt.addWidget(browse_cs_btn)

        # Layout ML.1.2 : Shaders
        self.__ui_shaders_cs_lyt = QtWidgets.QVBoxLayout()
        cs_lyt.addLayout(self.__ui_shaders_cs_lyt)

        # Layout ML.1.3 : Submit creation
        submit_creation_lyt = QtWidgets.QHBoxLayout()
        cs_lyt.addLayout(submit_creation_lyt)
        auto_assign_checkbox = QtWidgets.QCheckBox("Auto-assign by shader name")
        auto_assign_checkbox.setChecked(True)
        submit_creation_lyt.addWidget(auto_assign_checkbox, 0, QtCore.Qt.AlignRight)
        self.__ui_cs_submit_btn = QtWidgets.QPushButton("Create shaders")
        self.__ui_cs_submit_btn.setFixedSize(size_btn)
        self.__ui_cs_submit_btn.setEnabled(False)
        submit_creation_lyt.addWidget(self.__ui_cs_submit_btn, 0, QtCore.Qt.AlignLeft)

        # Layout ML.2.1 : Folder
        folder_us_lyt = QtWidgets.QHBoxLayout()
        us_lyt.addLayout(folder_us_lyt)
        self.__ui_us_folder_path = QtWidgets.QLineEdit()
        self.__ui_us_folder_path.setFixedHeight(btn_icon_size.height() + 3)
        self.__ui_us_folder_path.textChanged.connect(self.__on_folder_us_changed)
        folder_us_lyt.addWidget(self.__ui_us_folder_path)
        browse_us_btn = QtWidgets.QPushButton()
        browse_us_btn.setIconSize(icon_size)
        browse_us_btn.setFixedSize(btn_icon_size)
        browse_us_btn.setIcon(QtGui.QIcon(
            QtGui.QPixmap("C:/Users/m.jenin/Documents/marius/shader_maker/assets/browse.png")))  # TODO CHANGE
        browse_us_btn.clicked.connect(partial(self.__browse_us_folder))
        folder_us_lyt.addWidget(browse_us_btn)

        # Layout ML.2.2 : Selection files
        # TODO

        # Button ML.2.3 : Submit update
        self.__ui_us_submit_btn = QtWidgets.QPushButton("Update shaders")
        self.__ui_us_submit_btn.setFixedSize(size_btn)
        self.__ui_us_submit_btn.setEnabled(False)
        us_lyt.addWidget(self.__ui_us_submit_btn, 0, QtCore.Qt.AlignHCenter)

    def __update_ui(self):
        self.__refresh_btn()
        if self.__cs_folder_path is not None:
            self.__ui_cs_folder_path.setText(self.__cs_folder_path)
        if self.__us_folder_path is not None:
            self.__ui_us_folder_path.setText(self.__us_folder_path)

        if self.__ui_shaders_cs_lyt is not None:
            grid_shaders = QtWidgets.QGridLayout()
            scroll_area = QtWidgets.QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
            scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            scroll_area_widget = QtWidgets.QWidget()
            scroll_area.setWidget(scroll_area_widget)
            scroll_area_widget.setLayout(grid_shaders)
            self.__ui_shaders_cs_lyt.addWidget(scroll_area)

            index_row = 0
            index_col = 0
            nb_col = 3
            for shader in self.__cs_shaders:
                shader.populate(grid_shaders,index_row, index_col)
                if index_col == nb_col - 1:
                    index_col = 0
                    index_row += 1
                else:
                    index_col += 1

    # Refresh UI and model attribute when folder cs changes
    def __on_folder_cs_changed(self):
        folder_path = self.__ui_cs_folder_path.text()
        self.__cs_folder_path = folder_path if os.path.isdir(folder_path) else ""
        self.__load_cs_shaders()
        self.__update_ui()

    # Refresh UI and model attribute when folder us changes
    def __on_folder_us_changed(self):
        folder_path = self.__ui_us_folder_path.text()
        self.__us_folder_path = folder_path if os.path.isdir(folder_path) else ""
        self.__update_ui()

    def __load_cs_shaders(self):
        walk = list(os.walk("I:/battlestar_2206/assets\ch_panda/textures/02/panda_02_textures"))
        self.__cs_shaders.clear()
        for i in range(len(walk)-1):
            shader = Shader(walk[0][1][i])
            shader.load(walk[i+1][0])
            self.__cs_shaders.append(shader)

if __name__ == '__main__':
    ltp = ShaderMaker()
    ltp.show()
