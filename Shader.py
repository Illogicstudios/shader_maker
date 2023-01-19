import os
from os.path import isfile, join
import re

from pymel.core import *

from PySide2 import QtCore
from PySide2 import QtWidgets


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


class Shader:
    def __init__(self, title):
        self.__shader_fields = {
            "BaseColor": ShaderField(r".*(BaseColor).*\.exr"),
            "Normal": ShaderField(r"((?!Combine).)*(Normal)((?!Combine).)*\.exr"),
            "Height": ShaderField(r".*(Height).*\.exr"),
            "Roughness": ShaderField(r".*(Roughness).*\.exr"),
            "Metalness": ShaderField(r".*(Metalness).*\.exr"),
        }
        self.__title = title
        self.__ui_field_path = None
        self.__image_label = None

    # Getter of the title
    def get_title(self):
        return self.__title

    # Load the field according to the folder
    def load(self, folder_path):
        files_name_list = [f for f in os.listdir(folder_path) if
                           isfile(join(folder_path, f)) and re.match(r".*\.[exr]", f)]

        for keyword, field in self.__shader_fields.items():
            regexp = re.compile(field.get_regexp())
            for file_name in files_name_list:
                if re.match(regexp, file_name):
                    field.set_file_name(folder_path + "/" + file_name)
                    break

    # Populate the ui with the data of the shader
    def populate(self, layout, index_row, index_col, max_size):
        shader_card = QtWidgets.QVBoxLayout()
        shader_card.setMargin(5)
        frame_shader_card = QtWidgets.QFrame()
        frame_shader_card.setLayout(shader_card)
        frame_shader_card.setFrameShape(QtWidgets.QFrame.StyledPanel)
        frame_shader_card.setFrameShadow(QtWidgets.QFrame.Plain)

        shader_title = QtWidgets.QLabel(self.__title)
        shader_title.setMaximumWidth(max_size - 10)
        shader_title.setAlignment(QtCore.Qt.AlignCenter)
        shader_title.setMargin(5)
        shader_card.addWidget(shader_title)

        combobox = QtWidgets.QComboBox()
        combobox.activated[str].connect(self.on_combo_field_changed)

        shader_card.addWidget(combobox)
        self.__ui_field_path = QtWidgets.QLineEdit()
        self.__ui_field_path.setReadOnly(True)
        shader_card.addWidget(self.__ui_field_path)

        first = True
        for keyword, field in self.__shader_fields.items():
            if len(field.get_file_name()) > 0:
                if first:
                    self.on_combo_field_changed(keyword)
                    first = False
                combobox.addItem(keyword)

        layout.addWidget(frame_shader_card, index_row, index_col)

    # Change display filename when combobox item changed
    def on_combo_field_changed(self, text):
        file_name = self.__shader_fields[text].get_file_name()
        self.__ui_field_path.setText(file_name)

    # Generate the shader according to the data of the shader
    def generate_shading_nodes(self):
        place_texture = shadingNode("place2dTexture", asUtility=True, name="place2dTexture")

        arnold_node = shadingNode("aiStandardSurface", asShader=True, name=self.__title)

        base_color_file_name = self.__shader_fields["BaseColor"].get_file_name()
        roughness_file_name = self.__shader_fields["Normal"].get_file_name()
        metalness_file_name = self.__shader_fields["Height"].get_file_name()
        normal_file_name = self.__shader_fields["Roughness"].get_file_name()
        height_file_name = self.__shader_fields["Metalness"].get_file_name()

        # Base Color
        if len(base_color_file_name) > 0:
            base_color = shadingNode("file", asTexture=True, name="BaseColor")
            base_color.fileTextureName.set(base_color_file_name)
            place_texture.outUV >> base_color.uvCoord
            base_color.outColor >> arnold_node.baseColor

        # Roughness
        if len(roughness_file_name) > 0:
            roughness = shadingNode("file", asTexture=True, name="Roughness")
            roughness.fileTextureName.set(roughness_file_name)
            remap_value = shadingNode("remapValue", asUtility=True, name="remapValue")
            place_texture.outUV >> roughness.uvCoord
            roughness.outColorR >> remap_value.inputValue
            remap_value.outValue >> arnold_node.specularRoughness

        # Metalness
        if len(metalness_file_name) > 0:
            metalness = shadingNode("file", asTexture=True, name="Metalness")
            metalness.fileTextureName.set(metalness_file_name)
            place_texture.outUV >> metalness.uvCoord
            metalness.outColorR >> arnold_node.metalness

        # Normal
        if len(normal_file_name) > 0:
            normal = shadingNode("file", asTexture=True, name="Normal")
            normal.fileTextureName.set(normal_file_name)
            normal_map = shadingNode("aiNormalMap", asUtility=True, name="aiNormalMap")
            place_texture.outUV >> normal.uvCoord
            normal.outColor >> normal_map.input
            normal_map.outValue >> arnold_node.normalCamera

        # Height
        displacement_shader = None
        if len(height_file_name) > 0:
            height = shadingNode("file", asTexture=True, name="Height")
            height.fileTextureName.set(height_file_name)
            displacement_shader = shadingNode("displacementShader", asUtility=True, name="displacementShader")
            place_texture.outUV >> height.uvCoord
            height.outColorR >> displacement_shader.displacement
        return {arnold_node, displacement_shader}
