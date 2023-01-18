import os
import re
from functools import partial
from enum import Enum

from pymel.core import *
import maya.OpenMayaUI as omui

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

from shiboken2 import wrapInstance

from Shader import Shader, ShaderField
import utils


class Assignation(Enum):
    NoAssign = 1
    AutoAssign = 2
    AssignToSelection = 3


# CS mean create shaders part
# US mean update shaders part
class ShaderMaker(QtWidgets.QDialog):

    def __init__(self, parent=wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)):
        super(ShaderMaker, self).__init__(parent)

        # Model attributes
        self.__cs_folder_path = ""
        self.__cs_shaders = []
        self.__assign_cs = Assignation.AutoAssign
        self.__us_folder_path = ""

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
        self.__update_ui()
        self.__refresh_btn()

    # Reinitialize the ui in order to repopulate it
    def __reinit_ui(self):
        self.__ui_cs_folder_path = None
        self.__ui_us_folder_path = None
        self.__ui_cs_submit_btn = None
        self.__ui_us_submit_btn = None
        self.__ui_shaders_cs_lyt = None
        self.__auto_assign_radio = None
        self.__assign_to_selection_radio = None
        self.__no_assign_radio = None

    # Refresh the state of buttons
    def __refresh_btn(self):
        self.__ui_cs_submit_btn.setEnabled(len(self.__cs_shaders) > 0)
        self.__ui_us_submit_btn.setEnabled(False)  # TODO
        self.__assign_to_selection_radio.setEnabled(len(self.__cs_shaders) <= 1)
        if self.__assign_cs == Assignation.AssignToSelection:
            self.__auto_assign_radio.setChecked(True)

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
        self.setFixedSize(720, 800)
        self.move(QtWidgets.QDesktopWidget().availableGeometry().center() - self.frameGeometry().center())

        # Some aesthetic value
        size_btn = QtCore.QSize(180, 30)
        icon_size = QtCore.QSize(18, 18)
        btn_icon_size = QtCore.QSize(24, 24)

        # Main Layout
        main_lyt = QtWidgets.QVBoxLayout()
        main_lyt.setContentsMargins(10, 15, 10, 15)
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
        submit_creation_lyt.setAlignment(QtCore.Qt.AlignCenter)
        cs_lyt.addLayout(submit_creation_lyt)

        button_group_lyt = QtWidgets.QHBoxLayout()
        button_group_lyt.setAlignment(QtCore.Qt.AlignRight)
        button_group_cs = QtWidgets.QButtonGroup()
        self.__auto_assign_radio = QtWidgets.QRadioButton("Replace by shader name")
        self.__auto_assign_radio.setChecked(True)
        self.__assign_to_selection_radio = QtWidgets.QRadioButton("Assign to selection")
        self.__no_assign_radio = QtWidgets.QRadioButton("No assignation")
        self.__auto_assign_radio.toggled.connect(
            partial(self.__assign, Assignation.AutoAssign))
        self.__assign_to_selection_radio.toggled.connect(
            partial(self.__assign, Assignation.AssignToSelection))
        self.__no_assign_radio.toggled.connect(
            partial(self.__assign, Assignation.NoAssign))
        button_group_cs.addButton(self.__auto_assign_radio)
        button_group_cs.addButton(self.__assign_to_selection_radio)
        button_group_cs.addButton(self.__no_assign_radio)
        button_group_lyt.addWidget(self.__auto_assign_radio)
        button_group_lyt.addWidget(self.__assign_to_selection_radio)
        button_group_lyt.addWidget(self.__no_assign_radio)
        submit_creation_lyt.addLayout(button_group_lyt)

        self.__ui_cs_submit_btn = QtWidgets.QPushButton("Create shaders")
        self.__ui_cs_submit_btn.setFixedSize(size_btn)
        self.__ui_cs_submit_btn.setEnabled(False)
        self.__ui_cs_submit_btn.clicked.connect(self.__submit_create_shader)
        submit_creation_lyt.addWidget(self.__ui_cs_submit_btn)

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
        self.__ui_us_submit_btn.clicked.connect(self.__submit_update_shader())
        us_lyt.addWidget(self.__ui_us_submit_btn, 0, QtCore.Qt.AlignHCenter)

    def __update_ui(self):
        self.__refresh_btn()
        self.__ui_cs_folder_path.setText(self.__cs_folder_path)
        self.__ui_us_folder_path.setText(self.__us_folder_path)

        nb_shaders = len(self.__cs_shaders)
        if self.__ui_shaders_cs_lyt is not None:
            utils.clear_layout(self.__ui_shaders_cs_lyt)
            grid_shaders = QtWidgets.QGridLayout()
            scroll_area = QtWidgets.QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            grid_shaders.setAlignment(QtCore.Qt.AlignTop)
            scroll_area_widget = QtWidgets.QWidget()
            scroll_area.setWidget(scroll_area_widget)
            scroll_area_widget.setLayout(grid_shaders)
            self.__ui_shaders_cs_lyt.addWidget(scroll_area)
            if nb_shaders > 0:
                index_row = 0
                index_col = 0
                nb_col = 3
                if nb_shaders < nb_col:
                    max_size_elem = (680 - (nb_shaders - 1) * 15) / nb_shaders
                else:
                    max_size_elem = (680 - (nb_col - 1) * 15) / nb_col

                for shader in self.__cs_shaders:
                    shader.populate(grid_shaders, index_row, index_col, max_size_elem)
                    if index_col == nb_col - 1:
                        index_col = 0
                        index_row += 1
                    else:
                        index_col += 1

    # Refresh UI and model attribute when folder cs changes
    def __on_folder_cs_changed(self):
        folder_path = self.__ui_cs_folder_path.text()
        self.__cs_folder_path = folder_path
        self.__load_cs_shaders()
        self.__update_ui()

    # Refresh UI and model attribute when folder us changes
    def __on_folder_us_changed(self):
        folder_path = self.__ui_us_folder_path.text()
        self.__us_folder_path = folder_path
        self.__update_ui()

    def __load_cs_shaders(self):
        self.__cs_shaders.clear()
        if not os.path.isdir(self.__cs_folder_path):
            return
        child_dir = os.listdir(self.__cs_folder_path)
        list_dir = []
        has_exr = False
        for child in child_dir:
            if os.path.isdir(self.__cs_folder_path + "/" + child):
                list_dir.append(child)
            else:
                if re.match(r".*\.exr", child):
                    has_exr = True

        if len(list_dir) == 0:
            # If the folder is a shader folder
            if has_exr:
                shader = Shader(os.path.basename(self.__cs_folder_path))
                shader.load(self.__cs_folder_path)
                self.__cs_shaders.append(shader)
        else:
            # If the folder is a folder of shader folder
            for dir in list_dir:
                dir_path = self.__cs_folder_path + "/" + dir
                has_exr_2 = False
                child_dir_2 = os.listdir(dir_path)
                for child in child_dir_2:
                    if re.match(r".*\.exr", child):
                        has_exr_2 = True
                        break
                if has_exr_2:
                    shader = Shader(dir)
                    shader.load(dir_path)
                    self.__cs_shaders.append(shader)

    def __submit_create_shader(self):
        if self.__assign_cs == Assignation.AutoAssign:  # AutoAssign
            # Generate new shader
            shading_nodes = {}
            for shader in self.__cs_shaders:
                arnold_node, displacement_shader = shader.generate_shading_nodes()
                shading_nodes[shader.get_title()] = {arnold_node, displacement_shader}
            # Get all the shading groups to reassign
            to_reassign = {}
            selection = ls(materials=True)
            for s in selection:
                for shader in self.__cs_shaders:
                    if shader.get_title() == s.name():
                        shading_groups = s.listConnections(type="shadingEngine")
                        for shading_group in shading_groups:
                            if shading_group not in to_reassign:
                                to_reassign[shading_group] = shader.get_title()
                                break
            # Reassign the right to each shading group
            for shading_group, shader_title in to_reassign.items():
                delete(shading_group.surfaceShader.listConnections()[0])
                arnold_node, displacement_shader = shading_nodes[shader_title]
                arnold_node.outColor >> shading_group.surfaceShader
                displacement_shader.displacement >> shading_group.displacementShader

        elif self.__assign_cs == Assignation.AssignToSelection:  # AssignToSelection
            selection = ls(sl=True, transforms=True)
            # Create a new shading group
            shading_group = sets(name="SG", empty=True, renderable=True, noSurfaceShader=True)
            # Generate new shader and assign to shading group
            for shader in self.__cs_shaders:
                arnold_node, displacement_shader = shader.generate_shading_nodes()
                arnold_node.outColor >> shading_group.surfaceShader
                displacement_shader.displacement >> shading_group.displacementShader
            # Assign the object in the shading group
            for obj in selection:
                sets(shading_group, forceElement=obj)
        else:  # NoAssignation
            # Generate new shader
            for shader in self.__cs_shaders:
                shader.generate_shading_nodes()

    def __submit_update_shader(self):
        # TODO
        pass

    def __assign(self, assign_type, enabled):
        if enabled:
            self.__assign_cs = assign_type


if __name__ == '__main__':
    ltp = ShaderMaker()
    ltp.show()
