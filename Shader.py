import os
from os.path import isfile, join
import re

from functools import partial

from pymel.core import *

from PySide2 import QtCore
from PySide2 import QtWidgets

import ShaderMaker
from ShaderMaker import *


# A Texture field in the shader
class ShaderField:
    def __init__(self, rule):
        self.__regexp = re.compile(rule)
        self.__file_name = ""

    def get_file_name(self):
        return self.__file_name

    def set_file_name(self, file_name):
        self.__file_name = file_name

    def get_regexp(self):
        return self.__regexp

    def is_enabled(self):
        return len(self.__file_name) > 0


class Shader:
    def __init__(self, title):
        self.__shader_fields = {
            "BaseColor": ShaderField(r".*(BaseColor).*\.("+ShaderMaker.FILE_EXTENSION_SUPPORTED_REGEX+")"),
            "Normal": ShaderField(r"((?!Combine).)*(Normal)((?!Combine).)*\.("+ShaderMaker.FILE_EXTENSION_SUPPORTED_REGEX+")"),
            "Displacement": ShaderField(r".*(Height).*\.("+ShaderMaker.FILE_EXTENSION_SUPPORTED_REGEX+")"),
            "Roughness": ShaderField(r".*(Roughness).*\.("+ShaderMaker.FILE_EXTENSION_SUPPORTED_REGEX+")"),
            "Metalness": ShaderField(r".*(Metalness).*\.("+ShaderMaker.FILE_EXTENSION_SUPPORTED_REGEX+")"),
        }
        self.__title = title
        self.__dir_path = ""
        self.__ui_field_path = None
        self.__image_label = None
        self.__enabled = True

    # Getter of the title
    def get_title(self):
        return self.__title

    # Load the field according to the folder
    def load(self, folder_path):
        self.__dir_path = os.path.dirname(folder_path)
        files_name_list = [f for f in os.listdir(folder_path) if
                           isfile(join(folder_path, f)) and re.match(r".*\.("+ShaderMaker.FILE_EXTENSION_SUPPORTED_REGEX+")", f)]

        for keyword, field in self.__shader_fields.items():
            regexp = re.compile(field.get_regexp())
            for file_name in files_name_list:
                if re.match(regexp, file_name):
                    field.set_file_name(folder_path + "/" + file_name)
                    break

    # Populate the ui with the data of the shader
    def populate(self, shader_maker, layout, index_row, index_col, max_size):
        shader_card = QtWidgets.QVBoxLayout()
        shader_card.setMargin(5)
        frame_shader_card = QtWidgets.QFrame()
        frame_shader_card.setLayout(shader_card)
        frame_shader_card.setFrameShape(QtWidgets.QFrame.StyledPanel)
        frame_shader_card.setFrameShadow(QtWidgets.QFrame.Plain)

        top_layout = QtWidgets.QHBoxLayout()
        enabled_checkbox = QtWidgets.QCheckBox()
        enabled_checkbox.setChecked(True)
        enabled_checkbox.stateChanged.connect(partial(self.__enabled_changed,shader_maker))
        top_layout.addWidget(enabled_checkbox,0,QtCore.Qt.AlignLeft)

        shader_title = QtWidgets.QLabel(self.__title)
        shader_title.setMaximumWidth(max_size - 10)
        shader_title.setMargin(5)
        top_layout.addWidget(shader_title,1,QtCore.Qt.AlignCenter)

        shader_card.addLayout(top_layout)

        self.__ui_field_path = QtWidgets.QLineEdit(self.__dir_path)
        self.__ui_field_path.setReadOnly(True)
        shader_card.addWidget(self.__ui_field_path)

        grid_layout = QtWidgets.QGridLayout()
        i = 0
        for keyword, field in self.__shader_fields.items():
            if field.is_enabled():
                i += 1
                grid_layout.addWidget(QtWidgets.QLabel(keyword), i, 0)
                path_line = QtWidgets.QLineEdit(os.path.basename(field.get_file_name()))
                path_line.setReadOnly(True)
                grid_layout.addWidget(path_line, i, 1)

        shader_card.addLayout(grid_layout)
        layout.addWidget(frame_shader_card, index_row, index_col)

    def __enabled_changed(self,shader_maker,checked):
        self.__enabled = checked == QtCore.Qt.Checked
        shader_maker.refresh_btn()

    def is_enabled(self):
        return self.__enabled

    # Generate the shader according to the data of the shader
    def generate_shading_nodes(self):
        place_texture = shadingNode("place2dTexture", asUtility=True, name="place2dTexture")

        arnold_node = shadingNode("aiStandardSurface", asShader=True, name=self.__title)

        # Base Color
        if self.__shader_fields["BaseColor"].is_enabled():
            base_color_file_name = self.__shader_fields["BaseColor"].get_file_name()
            base_color = shadingNode("file", asTexture=True, name="BaseColor")
            base_color.fileTextureName.set(base_color_file_name)
            place_texture.outUV >> base_color.uvCoord
            base_color.outColor >> arnold_node.baseColor

        # Roughness
        if self.__shader_fields["Roughness"].is_enabled():
            roughness_file_name = self.__shader_fields["Normal"].get_file_name()
            roughness = shadingNode("file", asTexture=True, name="Roughness")
            roughness.fileTextureName.set(roughness_file_name)
            remap_value = shadingNode("remapValue", asUtility=True, name="remapValue")
            place_texture.outUV >> roughness.uvCoord
            roughness.outColorR >> remap_value.inputValue
            remap_value.outValue >> arnold_node.specularRoughness

        # Metalness
        if self.__shader_fields["Metalness"].is_enabled():
            metalness_file_name = self.__shader_fields["Displacement"].get_file_name()
            metalness = shadingNode("file", asTexture=True, name="Metalness")
            metalness.fileTextureName.set(metalness_file_name)
            place_texture.outUV >> metalness.uvCoord
            metalness.outColorR >> arnold_node.metalness

        # Normal
        if self.__shader_fields["Normal"].is_enabled():
            normal_file_name = self.__shader_fields["Roughness"].get_file_name()
            normal = shadingNode("file", asTexture=True, name="Normal")
            normal.fileTextureName.set(normal_file_name)
            normal_map = shadingNode("aiNormalMap", asUtility=True, name="aiNormalMap")
            place_texture.outUV >> normal.uvCoord
            normal.outColor >> normal_map.input
            normal_map.outValue >> arnold_node.normalCamera

        # Displacement
        displacement_node = None
        if self.__shader_fields["Displacement"].is_enabled():
            height_file_name = self.__shader_fields["Metalness"].get_file_name()
            height = shadingNode("file", asTexture=True, name="Displacement")
            height.fileTextureName.set(height_file_name)
            displacement_node = shadingNode("displacementShader", asUtility=True, name="displacementShader")
            place_texture.outUV >> height.uvCoord
            height.outColorR >> displacement_node.displacement
        return {arnold_node, displacement_node}
