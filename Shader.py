import os
from os.path import isfile, join
import re

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

class ShaderField:
    def __init__(self, title, rule):
        self.__title = title
        self.__regexp = re.compile(rule)
        self.__file_name = ""

    def get_title(self):
        return self.__title

    def get_file_name(self):
        return self.__file_name

    def set_file_name(self, file_name):
        self.__file_name = file_name

    def get_regexp(self):
        return self.__regexp


class Shader:
    def __init__(self, title):
        self.__shader_fields = [
            ShaderField("BaseColor", r".*(BaseColor).*\.exr"),
            ShaderField("Normal", r"((?!Combine).)*(Normal)((?!Combine).)*\.exr"),
            ShaderField("Height", r".*(Height).*\.exr"),
            ShaderField("Roughness", r".*(Roughness).*\.exr"),
            ShaderField("Metalness", r".*(Metalness).*\.exr"),
        ]
        self.__title = title

    def load(self, folder_path):
        files_name_list = [f for f in os.listdir(folder_path) if
                           isfile(join(folder_path, f)) and re.match(r".*\.[exr]", f)]

        for field in self.__shader_fields:
            regexp = re.compile(field.get_regexp())
            for file_name in files_name_list:
                if re.match(regexp, file_name):
                    field.set_file_name(file_name)
                    break

    def print(self):
        for field in self.__shader_fields:
            print(field.get_title()+" "+field.get_file_name())

    def populate(self, layout, index_row, index_col):
        shader_card = QtWidgets.QVBoxLayout()
        shader_card.setMargin(5)
        frame_shader_card = QtWidgets.QFrame()
        frame_shader_card.setLayout(shader_card)
        frame_shader_card.setFrameShape(QtWidgets.QFrame.StyledPanel)
        frame_shader_card.setFrameShadow(QtWidgets.QFrame.Plain)
        shader_title = QtWidgets.QLabel(self.__title)
        shader_title.setFont(QtGui.QFont('MS Sans Serif', 10))
        shader_title.setStyleSheet("font-weight:bold")
        shader_title.setMargin(5)
        shader_title.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        shader_card.addWidget(shader_title)
        combobox = QtWidgets.QComboBox()
        for field in self.__shader_fields:
            if len(field.get_file_name()) > 0 :
                combobox.addItem(field.get_title())


        shader_card.addWidget(combobox)

        layout.addWidget(frame_shader_card, index_row, index_col)
