import os
import re
from functools import partial

import sys

from pymel.core import *
import maya.OpenMayaUI as omui

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

from shiboken2 import wrapInstance

import utils

import maya.OpenMaya as OpenMaya

########################################################################################################################

DEFAULT_DIR_BROWSE = "I:/"

FILE_EXTENSION_SUPPORTED = ["exr", "jpg", "jpeg", "tif", "png"]

########################################################################################################################

FILE_EXTENSION_SUPPORTED_REGEX = "|".join(FILE_EXTENSION_SUPPORTED)

from Shader import Shader


def unload_packages(silent=True, packages=None):
    if packages is None:
        packages = []

    # construct reload list
    reload_list = []
    for i in sys.modules.keys():
        for package in packages:
            if i.startswith(package):
                reload_list.append(i)

    # unload everything
    for i in reload_list:
        try:
            if sys.modules[i] is not None:
                del (sys.modules[i])
                if not silent:
                    print("Unloaded: %s" % i)
        except:
            pass


class Assignation(Enum):
    NoAssign = 1
    AutoAssign = 2
    AssignToSelection = 3


# CS mean create shaders part
# US mean update shaders part
class ShaderMaker(QtWidgets.QDialog):

    @staticmethod
    def __get_dir_name():
        scene_name = sceneName()
        if len(scene_name) > 0:
            dirname = os.path.dirname(os.path.dirname(scene_name))
        else:
            dirname = DEFAULT_DIR_BROWSE
        return dirname

    def __init__(self, prnt=wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)):
        super(ShaderMaker, self).__init__(prnt)

        # Model attributes
        self.__cs_folder_path = ""
        self.__cs_shaders = []
        self.__assign_cs = Assignation.AutoAssign
        self.__us_folder_path = ""
        self.__us_data = {}

        # UI attributes
        self.__reinit_ui()

        # Retrieve us data
        self.__generate_us_data()

        # name the window
        self.setWindowTitle("Shader Maker")
        # make the window a "tool" in Maya's eyes so that it stays on top when you click off
        self.setWindowFlags(QtCore.Qt.Tool)
        # Makes the object get deleted from memory, not just hidden, when it is closed.
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # Create the layout, linking it to actions and refresh the display
        self.__create_ui()
        self.__refresh_ui()
        self.__create_callback()

    # Create a callback for when new Maya selection
    def __create_callback(self):
        self.__us_selection_callback = \
            OpenMaya.MEventMessage.addEventCallback("SelectionChanged", self.on_selection_changed)

    # Remove callback
    def closeEvent(self, arg__1: QtGui.QCloseEvent) -> None:
        OpenMaya.MMessage.removeCallback(self.__us_selection_callback)

    # initialize the ui
    def __reinit_ui(self):
        self.__ui_width = 900
        self.__ui_height = 800
        self.__ui_min_width = 700
        self.__ui_min_height = 400
        self.__ui_cs_nb_col = 1
        self.__ui_cs_folder_path = None
        self.__ui_us_folder_path = None
        self.__ui_cs_submit_btn = None
        self.__ui_us_submit_btn = None
        self.__ui_shaders_cs_lyt = None
        self.__auto_assign_radio = None
        self.__assign_to_selection_radio = None
        self.__no_assign_radio = None

    # Get the parent directory of the scene or a default one

    # Function to browse a new folder for the creation part
    def __browse_cs_folder(self):
        dirname = ShaderMaker.__get_dir_name()

        folder_path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Directory",
            dirname)
        if len(folder_path) > 0 and folder_path != self.__cs_folder_path:
            self.__ui_cs_folder_path.setText(folder_path)

    # Function to browse a new foler for the update part
    def __browse_us_folder(self):
        dirname = ShaderMaker.__get_dir_name()

        folder_path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Directory",
            dirname)
        if len(folder_path) > 0 and folder_path != self.__us_folder_path:
            self.__ui_us_folder_path.setText(folder_path)

    # Create the ui
    def __create_ui(self):
        # Reinit attributes of the UI
        self.__reinit_ui()
        self.setMinimumSize(self.__ui_min_width, self.__ui_min_height)
        self.resize(self.__ui_width, self.__ui_height)
        self.move(QtWidgets.QDesktopWidget().availableGeometry().center() - self.frameGeometry().center())

        browse_icon_path = os.path.dirname(__file__) + "/assets/browse.png"

        # Some aesthetic value
        size_btn = QtCore.QSize(180, 30)
        icon_size = QtCore.QSize(18, 18)
        btn_icon_size = QtCore.QSize(24, 24)

        # Main Layout
        main_lyt = QtWidgets.QHBoxLayout()
        main_lyt.setContentsMargins(10, 15, 10, 15)
        main_lyt.setSpacing(12)
        self.setLayout(main_lyt)

        # Layout ML.1 : Create shaders
        cs_lyt = QtWidgets.QVBoxLayout()
        cs_lyt.setAlignment(QtCore.Qt.AlignTop)
        main_lyt.addLayout(cs_lyt, 1)

        # Separator ML.1 | ML.2
        sep = QtWidgets.QFrame()
        sep.setMinimumWidth(1)
        sep.setFixedWidth(2)
        sep.setFrameShape(QtWidgets.QFrame.VLine)
        sep.setFrameShadow(QtWidgets.QFrame.Sunken)
        sep.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        main_lyt.addWidget(sep)

        # Layout ML.2 : Update shaders
        us_lyt = QtWidgets.QVBoxLayout()
        us_lyt.setAlignment(QtCore.Qt.AlignTop)
        main_lyt.addLayout(us_lyt, 1)

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
            QtGui.QPixmap(browse_icon_path)))
        browse_cs_btn.clicked.connect(partial(self.__browse_cs_folder))
        folder_cs_lyt.addWidget(browse_cs_btn)

        # Layout ML.1.2 : Shaders
        self.__ui_shaders_cs_lyt = QtWidgets.QVBoxLayout()
        cs_lyt.addLayout(self.__ui_shaders_cs_lyt)

        # Layout ML.1.3 : Submit creation
        submit_creation_lyt = QtWidgets.QHBoxLayout()
        submit_creation_lyt.setAlignment(QtCore.Qt.AlignCenter)
        cs_lyt.addLayout(submit_creation_lyt)

        button_group_lyt = QtWidgets.QVBoxLayout()
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
            QtGui.QPixmap(browse_icon_path)))
        browse_us_btn.clicked.connect(partial(self.__browse_us_folder))
        folder_us_lyt.addWidget(browse_us_btn)

        # Layout ML.2.2 : Selection files
        self.__ui_tree_us_files = QtWidgets.QTreeWidget()
        self.__ui_tree_us_files.setHeaderHidden(True)
        us_lyt.addWidget(self.__ui_tree_us_files)

        # Button ML.2.3 : Submit update
        self.__ui_us_submit_btn = QtWidgets.QPushButton("Update shaders")
        self.__ui_us_submit_btn.setFixedSize(size_btn)
        self.__ui_us_submit_btn.setEnabled(False)
        self.__ui_us_submit_btn.clicked.connect(self.__submit_update_shader)
        us_lyt.addWidget(self.__ui_us_submit_btn, 0, QtCore.Qt.AlignHCenter)

    # Refresh the ui according to the model attribute
    def __refresh_ui(self):
        # Refresh browser
        self.__ui_cs_folder_path.setText(self.__cs_folder_path)
        self.__ui_us_folder_path.setText(self.__us_folder_path)

        self.refresh_btn()

        self.__refresh_cs_body()

        self.__refresh_us_body()

    def refresh_btn(self):
        nb_shader_enabled = 0
        for shader in self.__cs_shaders:
            if shader.is_enabled():
                nb_shader_enabled += 1
        # Refresh the buttons
        if self.__ui_cs_submit_btn is not None:
            self.__ui_cs_submit_btn.setEnabled(nb_shader_enabled > 0)
        if self.__assign_to_selection_radio is not None:
            self.__assign_to_selection_radio.setEnabled(nb_shader_enabled <= 1)
        if self.__assign_cs == Assignation.AssignToSelection and nb_shader_enabled > 1:
            self.__auto_assign_radio.setChecked(True)

    def __refresh_cs_body(self):
        # Refresh the body of the creation part
        nb_shaders = len(self.__cs_shaders)
        if self.__ui_shaders_cs_lyt is not None:
            utils.clear_layout(self.__ui_shaders_cs_lyt)
            grid_shaders = QtWidgets.QGridLayout()
            scroll_area = QtWidgets.QScrollArea()
            scroll_area.setWidgetResizable(True)
            grid_shaders.setAlignment(QtCore.Qt.AlignTop)
            scroll_area_widget = QtWidgets.QWidget()
            scroll_area.setWidget(scroll_area_widget)
            scroll_area_widget.setLayout(grid_shaders)
            self.__ui_shaders_cs_lyt.addWidget(scroll_area)
            width = self.width()
            if nb_shaders > 0:
                index_row = 0
                index_col = 0
                if nb_shaders < self.__ui_cs_nb_col:
                    max_size_elem = (width - 40 - (nb_shaders - 1) * 15) / nb_shaders
                else:
                    max_size_elem = (width - 40 - (self.__ui_cs_nb_col - 1) * 15) / self.__ui_cs_nb_col

                for shader in self.__cs_shaders:
                    shader.populate(self, grid_shaders, index_row, index_col, max_size_elem)
                    if index_col == self.__ui_cs_nb_col - 1:
                        index_col = 0
                        index_row += 1
                    else:
                        index_col += 1

    def __refresh_us_body(self):
        # Refresh the body of the update part
        if self.__ui_tree_us_files is not None:
            self.__ui_tree_us_files.clear()
            update_btn_enabled = False
            for directory, data in self.__us_data.items():
                textures = data[0]
                shaders = data[1]
                dir_string = directory + "     ["
                nb_shaders = len(shaders)
                for i in range(len(shaders)):
                    dir_string += shaders[i].name()
                    if i != nb_shaders - 1:
                        dir_string += ", "
                dir_string += "]"

                item = QtWidgets.QTreeWidgetItem([dir_string])
                self.__ui_tree_us_files.addTopLevelItem(item)
                for texture in textures:
                    filepath = texture.getAttr("fileTextureName")
                    filename = os.path.basename(filepath)
                    child = QtWidgets.QTreeWidgetItem([filename])
                    child_enabled = os.path.exists(self.__us_folder_path + "/" + filename)
                    update_btn_enabled |= child_enabled
                    child.setDisabled(not child_enabled)
                    item.addChild(child)
                item.setExpanded(True)

            # Refresh the update button according to the update body
            if self.__ui_us_submit_btn is not None:
                self.__ui_us_submit_btn.setEnabled(
                    len(self.__us_data) > 0 and os.path.isdir(self.__us_folder_path) and update_btn_enabled)

    # Refresh UI and model attribute when the fodler of the creation part changes
    def __on_folder_cs_changed(self):
        folder_path = self.__ui_cs_folder_path.text()
        self.__cs_folder_path = folder_path
        self.__generate_cs_shaders()
        self.__refresh_ui()

    # Refresh UI and model attribute when the fodler of the update part changes
    def __on_folder_us_changed(self):
        folder_path = self.__ui_us_folder_path.text()
        self.__us_folder_path = folder_path
        self.__generate_us_data()
        self.__refresh_ui()

    # Function called by the callback of the Maya selection
    def on_selection_changed(self, *args, **kwargs):
        self.__generate_us_data()
        self.__refresh_us_body()

    # Get the textures and the shading groups of the selection
    def __get_us_shading_groups_and_textures(self):
        files = []
        selection = ls(sl=True, transforms=True)
        distinct_shading_groups = []
        for s in selection:
            shape = s.getShape()
            if shape is not None:
                shading_groups = shape.listConnections(type="shadingEngine")
                for shading_group in shading_groups:
                    if shading_group not in distinct_shading_groups:
                        distinct_shading_groups.append(shading_group)

        for shading_group in distinct_shading_groups:
            textures = self.__get_textures_recursive(shading_group)
            for texture in textures:
                files.append({texture, shading_group})
        return files

    # Get the textures from a node recursively
    def __get_textures_recursive(self, node):
        textures = []
        connections = node.listConnections(source=True, destination=False)
        for connection in connections:
            if connection.type() == 'file':
                textures.append(connection)
            else:
                textures.extend(self.__get_textures_recursive(connection))
        return textures

    # Generate model data for the update part
    def __generate_us_data(self):
        self.__us_data.clear()
        for texture, shading_group in self.__get_us_shading_groups_and_textures():
            dirname = os.path.dirname(texture.getAttr("fileTextureName"))
            if dirname not in self.__us_data:
                self.__us_data[dirname] = [[], []]
            self.__us_data[dirname][0].append(texture)

            if shading_group not in self.__us_data[dirname][1]:
                self.__us_data[dirname][1].append(shading_group)

    # Generate the model data for the creatino part
    def __generate_cs_shaders(self):
        self.__cs_shaders.clear()
        if not os.path.isdir(self.__cs_folder_path):
            return
        child_dir = os.listdir(self.__cs_folder_path)
        list_dir = []
        has_texture = False

        for child in child_dir:
            if os.path.isdir(self.__cs_folder_path + "/" + child):
                list_dir.append(child)
            else:
                if re.match(r".*\.(" + FILE_EXTENSION_SUPPORTED_REGEX + ")", child):
                    has_texture = True

        if has_texture:
            # If the folder is a shader folder
            shader = Shader(os.path.basename(self.__cs_folder_path))
            sub_shaders = shader.load(self.__cs_folder_path)
            if len(sub_shaders) > 0:
                self.__cs_shaders.extend(sub_shaders)
            else:
                self.__cs_shaders.append(shader)
        else:
            # If the folder is a folder of shader folder
            for directory in list_dir:
                dir_path = self.__cs_folder_path + "/" + directory
                has_texture_2 = False
                child_dir_2 = os.listdir(dir_path)
                for child in child_dir_2:
                    if re.match(r".*\.(" + FILE_EXTENSION_SUPPORTED_REGEX + ")", child):
                        has_texture_2 = True
                        break
                if has_texture_2:
                    shader = Shader(directory)
                    sub_shaders = shader.load(dir_path)
                    if len(sub_shaders) > 0:
                        self.__cs_shaders.extend(sub_shaders)
                    else:
                        self.__cs_shaders.append(shader)

    # Create the shader according to the method of assignation
    def __submit_create_shader(self):
        undoInfo(openChunk = True)
        no_items_to_assign = False
        if self.__assign_cs == Assignation.AutoAssign:  # AutoAssign
            # Get all the shading groups to reassign
            to_reassign = {}
            selection = ls(materials=True)
            for s in selection:
                for shader in self.__cs_shaders:
                    if shader.is_enabled() and shader.get_title() == s.name():
                        shading_groups = s.listConnections(type="shadingEngine")
                        for shading_group in shading_groups:
                            if shading_group not in to_reassign:
                                to_reassign[shading_group] = shader.get_title()
                                break
            no_items_to_assign = len(to_reassign) == 0
            if not no_items_to_assign:
                # Reassign the right to each shading group
                for shading_group, shader_title in to_reassign.items():
                    self.__delete_existing_shader(shading_group)

                shading_nodes = {}
                for shader in self.__cs_shaders:
                    if shader.is_enabled():
                        arnold_node, displacement_node = shader.generate_shading_nodes()
                        shading_nodes[shader.get_title()] = {arnold_node, displacement_node}

                for shading_group, shader_title in to_reassign.items():
                    arnold_node, displacement_node = shading_nodes[shader_title]
                    arnold_node.outColor >> shading_group.surfaceShader
                    displacement_node.displacement >> shading_group.displacementShader

        elif self.__assign_cs == Assignation.AssignToSelection:  # AssignToSelection
            selection = ls(sl=True, transforms=True)
            no_items_to_assign = len(selection) == 0
            if not no_items_to_assign:
                # Create a new shading group
                shading_group = sets(name="SG", empty=True, renderable=True, noSurfaceShader=True)
                # Generate new shader and assign to shading group
                for shader in self.__cs_shaders:
                    if shader.is_enabled():
                        arnold_node, displacement_node = shader.generate_shading_nodes()
                        arnold_node.outColor >> shading_group.surfaceShader
                        displacement_node.displacement >> shading_group.displacementShader
                # Assign the object in the shading group
                for obj in selection:
                    sets(shading_group, forceElement=obj)
        if self.__assign_cs == Assignation.NoAssign or no_items_to_assign:  # NoAssignation
            dtx = 1
            i = 0
            # Generate new shader and assign each to an object
            for shader in self.__cs_shaders:
                if shader.is_enabled():
                    obj = sphere()[0]
                    obj.translate.set([dtx * i, 0, 0])

                    shading_group = sets(name=shader.get_title()+"_sg", empty=True, renderable=True, noSurfaceShader=True)
                    arnold_node, displacement_node = shader.generate_shading_nodes()
                    arnold_node.outColor >> shading_group.surfaceShader
                    if displacement_node is not None:
                        displacement_node.displacement >> shading_group.displacementShader
                    sets(shading_group, forceElement=obj)
                    i += 1
        undoInfo(closeChunk = True)

    # Delete an existing shader recursively
    def __delete_existing_shader(self, node):
        for s in node.inputs():
            if s.type() != "transform":
                self.__delete_existing_shader(s)
                try:
                    if "default" not in s.name():
                        delete(s)
                except:
                    pass

    # Update file path with model datas
    def __submit_update_shader(self):
        undoInfo(openChunk = True)
        for directory, data in self.__us_data.items():
            textures = data[0]
            for texture in textures:
                filepath = texture.getAttr("fileTextureName")
                filename = os.path.basename(filepath)
                child_enabled = os.path.exists(self.__us_folder_path + "/" + filename)
                if child_enabled:
                    texture.fileTextureName.set(self.__us_folder_path + "/" + filename)
        undoInfo(closeChunk = True)

    # Change the Assignation type
    def __assign(self, assign_type, enabled):
        if enabled:
            self.__assign_cs = assign_type
