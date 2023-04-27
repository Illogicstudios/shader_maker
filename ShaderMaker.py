import os
import re
from enum import Enum
from functools import partial

import sys

import pymel.core as pm
import maya.OpenMayaUI as omui

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

from shiboken2 import wrapInstance

from common.utils import *
from common.Prefs import *

import maya.OpenMaya as OpenMaya

########################################################################################################################

_FILE_NAME_PREFS = "shader_maker"

DEFAULT_DIR_BROWSE = "I:/"

FILE_EXTENSION_SUPPORTED = ["exr", "jpg", "jpeg", "tif", "png", "tx"]

DEFAULT_DISPLACEMENT_SCALE = 0.02
DEFAULT_DISPLACEMENT_MID = 0

########################################################################################################################

FILE_EXTENSION_SUPPORTED_REGEX = "|".join(FILE_EXTENSION_SUPPORTED)

from .Shader import Shader


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
        scene_name = pm.sceneName()
        if len(scene_name) > 0:
            dirname = os.path.dirname(os.path.dirname(scene_name))
        else:
            dirname = DEFAULT_DIR_BROWSE
        return dirname

    def __init__(self, prnt=wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)):
        super(ShaderMaker, self).__init__(prnt)

        # Common Preferences (common preferences on all tools)
        self.__common_prefs = Prefs()
        # Preferences for this tool
        self.__prefs = Prefs(_FILE_NAME_PREFS)

        # Model attributes
        self.__cs_folder_path = ""
        self.__cs_shaders = []
        self.__assign_cs = Assignation.AutoAssign
        self.__us_folder_path = ""
        self.__us_data = {}
        self.__displacement_scale = DEFAULT_DISPLACEMENT_SCALE
        self.__displacement_mid = DEFAULT_DISPLACEMENT_MID

        # UI attributes
        self.__ui_width = 750
        self.__ui_height = 700
        self.__ui_min_width = 750
        self.__ui_min_height = 200
        self.__ui_pos = QDesktopWidget().availableGeometry().center() - QPoint(self.__ui_width,self.__ui_height)/2
        self.__ui_cs_folder_path = None
        self.__ui_us_folder_path = None
        self.__ui_cs_submit_btn = None
        self.__ui_us_submit_btn = None
        self.__ui_shaders_cs_lyt = None
        self.__auto_assign_radio = None
        self.__assign_to_selection_radio = None
        self.__no_assign_radio = None

        self.__retrieve_prefs()

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


    # Save preferences
    def __save_prefs(self):
        size = self.size()
        self.__prefs["window_size"] = {"width": size.width(), "height": size.height()}
        pos = self.pos()
        self.__prefs["window_pos"] = {"x": pos.x(), "y": pos.y()}

    # Retrieve preferences
    def __retrieve_prefs(self):
        if "window_pos" in self.__prefs:
            pos = self.__prefs["window_pos"]
            self.__ui_pos = QPoint(pos["x"],pos["y"])


    # Create a callback for when new Maya selection
    def __create_callback(self):
        self.__us_selection_callback = \
            OpenMaya.MEventMessage.addEventCallback("SelectionChanged", self.on_selection_changed)

    # Remove callback
    def hideEvent(self, arg__1: QtGui.QCloseEvent) -> None:
        OpenMaya.MMessage.removeCallback(self.__us_selection_callback)
        self.__save_prefs()


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
        self.setMinimumSize(self.__ui_min_width, self.__ui_min_height)
        self.resize(self.__ui_width, self.__ui_height)
        self.move(self.__ui_pos)

        browse_icon_path = os.path.dirname(__file__) + "/assets/browse.png"

        # Some aesthetic value
        size_btn = QtCore.QSize(180, 40)
        icon_size = QtCore.QSize(18, 18)
        btn_icon_size = QtCore.QSize(24, 24)

        main_lyt = QtWidgets.QVBoxLayout()
        self.setLayout(main_lyt)
        tab_widget = QtWidgets.QTabWidget()
        main_lyt.addWidget(tab_widget)

        # Layout ML.1 : Create shaders
        cs_lyt = QtWidgets.QVBoxLayout()
        cs_lyt.setSpacing(4)
        cs_lyt.setMargin(5)
        cs_lyt.setAlignment(QtCore.Qt.AlignTop)
        cs_widget = QtWidgets.QWidget()
        cs_widget.setLayout(cs_lyt)
        tab_widget.addTab(cs_widget, "Create Shader")

        # Layout ML.2 : Update shaders
        us_lyt = QtWidgets.QVBoxLayout()
        us_lyt.setSpacing(4)
        us_lyt.setMargin(5)
        us_lyt.setAlignment(QtCore.Qt.AlignTop)
        us_widget = QtWidgets.QWidget()
        us_widget.setLayout(us_lyt)
        tab_widget.addTab(us_widget, "Update Texture Paths")

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

        # Layout ML.1.2 : Header
        self.__ui_widget_header = QtWidgets.QWidget()
        header_shaders_cs_lyt = QtWidgets.QVBoxLayout(self.__ui_widget_header)
        header_shaders_cs_lyt.setMargin(0)
        Shader.generate_header(self, header_shaders_cs_lyt)
        self.__ui_widget_header.setVisible(True)
        cs_lyt.addWidget(self.__ui_widget_header)

        # Layout ML.1.3 : Shaders
        self.__ui_shaders_cs_lyt = QtWidgets.QVBoxLayout()
        cs_lyt.addLayout(self.__ui_shaders_cs_lyt)

        # Layout ML.1.4 : Displacement scale
        displacement_scale_form = QtWidgets.QFormLayout()
        validator = QtGui.QRegExpValidator(QtCore.QRegExp(r"[0-9]+(\.[0-9]*)?"))
        displacement_scale_edit = QtWidgets.QLineEdit(str(self.__displacement_scale))
        displacement_scale_edit.setValidator(validator)
        displacement_scale_edit.textChanged.connect(self.__displacement_scale_changed)
        displacement_mid_edit = QtWidgets.QLineEdit(str(self.__displacement_mid))
        displacement_mid_edit.setValidator(validator)
        displacement_mid_edit.textChanged.connect(self.__displacement_mid_changed)
        displacement_scale_form.addRow(QtWidgets.QLabel("Displacement scale"), displacement_scale_edit)
        displacement_scale_form.addRow(QtWidgets.QLabel("Displacement mid"), displacement_mid_edit)
        cs_lyt.addLayout(displacement_scale_form)

        # Layout ML.1.5 : Submit creation
        submit_creation_lyt = QtWidgets.QHBoxLayout()
        submit_creation_lyt.setAlignment(QtCore.Qt.AlignCenter)
        submit_creation_lyt.setMargin(5)
        cs_lyt.addLayout(submit_creation_lyt)

        button_group_lyt = QtWidgets.QHBoxLayout()
        button_group_lyt.setAlignment(QtCore.Qt.AlignCenter)
        button_group_lyt.setMargin(5)
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
        submit_creation_lyt.addWidget(self.__ui_cs_submit_btn, QtCore.Qt.AlignRight)

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
        self.__ui_us_submit_btn = QtWidgets.QPushButton("Update Texture Paths")
        self.__ui_us_submit_btn.setFixedSize(size_btn)
        self.__ui_us_submit_btn.setEnabled(False)
        self.__ui_us_submit_btn.clicked.connect(self.__submit_update_shader)
        us_lyt.addWidget(self.__ui_us_submit_btn, 0, QtCore.Qt.AlignHCenter)

    def __displacement_scale_changed(self, value):
        if len(value) > 0:
            self.__displacement_scale = float(value)

    def __displacement_mid_changed(self, value):
        if len(value) > 0:
            self.__displacement_mid = float(value)

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
        self.__ui_widget_header.setVisible(nb_shaders > 0)
        if self.__ui_shaders_cs_lyt is not None:
            clear_layout(self.__ui_shaders_cs_lyt)
            list_shaders_lyt = QtWidgets.QVBoxLayout()
            list_shaders_lyt.setContentsMargins(2, 2, 2, 2)
            list_shaders_lyt.setSpacing(2)
            list_shaders_lyt.setAlignment(QtCore.Qt.AlignTop)
            scroll_area = QtWidgets.QScrollArea()
            scroll_area.setWidgetResizable(True)
            list_shaders_lyt.setAlignment(QtCore.Qt.AlignTop)
            scroll_area_widget = QtWidgets.QWidget()
            scroll_area.setWidget(scroll_area_widget)
            scroll_area_widget.setLayout(list_shaders_lyt)
            self.__ui_shaders_cs_lyt.addWidget(scroll_area)
            if nb_shaders > 0:
                for shader in self.__cs_shaders:
                    shader.populate(self, list_shaders_lyt)

    def __refresh_us_body(self):
        # Refresh the body of the update part
        textures_displayed= {}
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

                if directory not in textures_displayed:
                    textures_displayed[directory] = []

                item = QtWidgets.QTreeWidgetItem([dir_string])
                self.__ui_tree_us_files.addTopLevelItem(item)
                for texture in textures:
                    filepath = texture.getAttr("fileTextureName")
                    if filepath not in textures_displayed[directory]:
                        textures_displayed[directory].append(filepath)

                        filename = os.path.basename(filepath)
                        child = QtWidgets.QTreeWidgetItem([filename])

                        base = re.search("(.*)(?:<UDIM>|[0-9]{4})\.(?:" + FILE_EXTENSION_SUPPORTED_REGEX + ")", filename)
                        match = base.groups()[0]
                        regex = match.replace(".", "\.") + "((?:[0-9]{0,4})\.(?:" + FILE_EXTENSION_SUPPORTED_REGEX + "))"
                        new_file_path = self.__us_find_file_in_directory(
                            self.__us_folder_path, regex)

                        child_enabled = new_file_path is not None and new_file_path != filepath
                        update_btn_enabled |= child_enabled
                        child.setDisabled(not child_enabled)
                        item.addChild(child)
                item.setExpanded(True)

            # Refresh the update button according to the update body
            if self.__ui_us_submit_btn is not None:
                self.__ui_us_submit_btn.setEnabled(
                    len(self.__us_data) > 0 and os.path.isdir(self.__us_folder_path) and update_btn_enabled)
                self.__ui_us_submit_btn.setEnabled(True)

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
        selection = pm.ls(sl=True, transforms=True)
        distinct_shading_groups = []
        for s in selection:
            for shape in s.listRelatives(shapes=True, allDescendents=True):
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
                if re.match(r".*\.(?:" + FILE_EXTENSION_SUPPORTED_REGEX + ")", child):
                    has_texture = True

        if has_texture:
            # If the folder is a shader folder
            shaders = Shader(os.path.basename(self.__cs_folder_path)).load(self.__cs_folder_path)
            for shad, nb in shaders:
                if nb > 0:
                    self.__cs_shaders.append(shad)
        else:
            # If the folder is a folder of shader folder
            for directory in list_dir:
                dir_path = self.__cs_folder_path + "/" + directory
                has_texture_2 = False
                child_dir_2 = os.listdir(dir_path)
                for child in child_dir_2:
                    if re.match(r".*\.(?:" + FILE_EXTENSION_SUPPORTED_REGEX + ")", child):
                        has_texture_2 = True
                        break
                if has_texture_2:
                    shaders = Shader(directory).load(dir_path)
                    for shad, nb in shaders:
                        if nb > 0:
                            self.__cs_shaders.append(shad)

    def __get_shading_values(self):
        return {
            "displacement_scale": self.__displacement_scale,
            "displacement_mid": self.__displacement_mid
        }

    # Create the shader according to the method of assignation
    def __submit_create_shader(self):
        pm.undoInfo(openChunk=True)
        no_items_to_assign = False
        shading_values = self.__get_shading_values()
        if self.__assign_cs == Assignation.AutoAssign:  # AutoAssign
            # Get all the shading groups to reassign
            to_reassign = {}
            selection = pm.ls(materials=True)
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
                        arnold_node, displacement_node = shader.generate_shading_nodes(shading_values)
                        shading_nodes[shader.get_title()] = {arnold_node, displacement_node}

                for shading_group, shader_title in to_reassign.items():
                    arnold_node, displacement_node = shading_nodes[shader_title]
                    arnold_node.outColor >> shading_group.surfaceShader
                    if displacement_node is not None:
                        displacement_node.displacement >> shading_group.displacementShader

        elif self.__assign_cs == Assignation.AssignToSelection:  # AssignToSelection
            selection = pm.ls(sl=True, transforms=True)
            no_items_to_assign = len(selection) == 0
            if not no_items_to_assign:
                # Create a new shading group
                shading_group = pm.sets(name="SG", empty=True, renderable=True, noSurfaceShader=True)
                # Generate new shader and assign to shading group
                for shader in self.__cs_shaders:
                    if shader.is_enabled():
                        arnold_node, displacement_node = shader.generate_shading_nodes(shading_values)
                        arnold_node.outColor >> shading_group.surfaceShader
                        if displacement_node is not None:
                            displacement_node.displacement >> shading_group.displacementShader
                # Assign the object in the shading group
                for obj in selection:
                    pm.sets(shading_group, forceElement=obj)
        if self.__assign_cs == Assignation.NoAssign or no_items_to_assign:  # NoAssignation
            dtx = 1
            i = 0
            # Generate new shader and assign each to an object
            for shader in self.__cs_shaders:
                if shader.is_enabled():
                    obj = pm.sphere()[0]
                    obj.translate.set([dtx * i, 0, 0])

                    shading_group = pm.sets(name=shader.get_title() + "_sg", empty=True, renderable=True,
                                         noSurfaceShader=True)
                    arnold_node, displacement_node = shader.generate_shading_nodes(shading_values)
                    arnold_node.outColor >> shading_group.surfaceShader
                    if displacement_node is not None:
                        displacement_node.displacement >> shading_group.displacementShader
                    pm.sets(shading_group, forceElement=obj)
                    i += 1
        pm.undoInfo(closeChunk=True)

    # Delete an existing shader recursively
    def __delete_existing_shader(self, node):
        for s in node.inputs():
            if pm.objExists(s):
                if s.type() != "transform":
                    self.__delete_existing_shader(s)
                    try:
                        if "default" not in s.name():
                            pm.delete(s)
                    except:
                        pass
        print("Existing shaders deleted")

    # Update file path with model datas
    def __submit_update_shader(self):
        pm.undoInfo(openChunk=True)
        for directory, data in self.__us_data.items():
            textures = data[0]
            for texture in textures:
                filepath = texture.getAttr("fileTextureName")
                filename = os.path.basename(filepath)

                base = re.search("(.*)(?:<UDIM>|[0-9]{4})\.(?:" + FILE_EXTENSION_SUPPORTED_REGEX + ")", filename)
                match = base.groups()[0]
                regex = match.replace(".", "\.") + "((?:[0-9]{0,4})\.(?:" + FILE_EXTENSION_SUPPORTED_REGEX + "))"

                new_file_path = self.__us_find_file_in_directory(self.__us_folder_path, regex)
                if new_file_path is not None and new_file_path != filepath:
                    texture.fileTextureName.set(new_file_path)
        self.__generate_us_data()
        self.__refresh_us_body()
        pm.undoInfo(closeChunk=True)

    def __us_find_file_in_directory(self, directory, regex, depth=4):
        if depth > 0:
            filename = None
            if os.path.isdir(directory):
                for f in os.listdir(directory):
                    if os.path.isfile(directory+"/"+f):
                        match = re.match(regex, f)
                        if match is not None:
                            filename = match.group()
                            break
            if filename is not None:
                return directory + "/" + filename
            else:
                if os.path.exists(directory):
                    for d in os.scandir(directory):
                        if d.is_dir():
                            filepath = self.__us_find_file_in_directory(d.path.replace('\\', '/'), regex, depth - 1)
                            if filepath is not None:
                                return filepath
        return None

    def set_all_shaders_enabled(self, enabled):
        for shader in self.__cs_shaders:
            shader.set_enabled(enabled)

    def set_all_field_enabled(self, keyword, enabled):
        for shader in self.__cs_shaders:
            shader.set_field_enabled(keyword, enabled)

    # Change the Assignation type
    def __assign(self, assign_type, enabled):
        if enabled:
            self.__assign_cs = assign_type
