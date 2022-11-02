import math
import os
from os import listdir
from os.path import isfile, join

import maya.cmds as cmds
import maya.OpenMayaUI as omui
import maya.mel as mel

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

from shiboken2 import wrapInstance


class ShaderMaker(QtWidgets.QDialog):
    # Retrieve the selected light or create one
    def __init__(self, parent=wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)):
        super(ShaderMaker, self).__init__(parent)

        # Model attributes
        self.__selected_list = []
        self.__folder_path = None
        self.__texture_list = []

        # UI attributes
        self.__reinit_ui()

        # Setup model attributes
        self.__retrieve_selected()

        # name the window
        self.setWindowTitle("Shader Maker")
        # make the window a "tool" in Maya's eyes so that it stays on top when you click off
        self.setWindowFlags(QtCore.Qt.Tool)
        # Makes the object get deleted from memory, not just hidden, when it is closed.
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # Create the layout and linking it to actions
        self.__create_layout()
        self.__link_actions()

    def is_valid_to_assign(self):
        return len(self.__selected_list) > 0

    # If lights are selected we take them
    def __retrieve_selected(self):
        self.__selected_list = cmds.ls(sl=True, dag=True)

    # Attach the texture light to the lights
    def attach_texture(self):
        pass
        # if len(self.__lights_selected) > 0:
        #     render_node = self.__create_render_node_texture()
        #     for light in self.__lights_selected:
        #         attr_light = light + '.color'
        #         # Get all the connections for the color attribute of the light and disconnect them
        #         conns_lights = cmds.listConnections(attr_light, plugs=True, destination=False) or []
        #         if conns_lights:
        #             for conn in conns_lights:
        #                 cmds.disconnectAttr(conn, attr_light)
        #         # Connect the new texture
        #         cmds.connectAttr(render_node + '.outColor', light + '.color')

    # Remove the texture of lights
    def remove_textures(self):
        pass
        # for light in self.__lights_selected:
        #     attr_light = light + '.color'
        #     # Get all the connections for the color attribute of the light and disconnect them
        #     conns_lights = cmds.listConnections(attr_light, plugs=True, destination=False) or []
        #     if conns_lights:
        #         for conn in conns_lights:
        #             cmds.disconnectAttr(conn, attr_light)
        #         cmds.setAttr(attr_light, 1, 1, 1, type='double3')
        #
        #     # Create a Render Node for a file

    def __create_render_node_texture(self):
        pass
        # render_node = cmds.shadingNode("file", asTexture=True, asUtility=True)
        # #SWITCH TO TX
        # parentDir =os.path.dirname(os.path.dirname(self.__texture))
        # filename = os.path.basename(self.__texture)
        # filenameTX =  os.path.splitext(filename)[0]+".tx"
        # pathTX= os.path.join(parentDir,filenameTX)
        #
        # cmds.setAttr(render_node + '.fileTextureName', pathTX,
        #              type="string")
        # return render_node

    def __select_lights(self):
        pass
        # cmds.select(clear=True)
        # for light in self.__lights_selected:
        #     cmds.select(light, add=True)

    def __reinit_ui(self):
        self.__ui_folder = None
        self.__ui_layout_textures = None
        self.__ui_dropdown_shader_plug_list = []
        self.__ui_btn_folder = None
        self.__ui_btn_submit = None

    # Create the layout
    def __create_layout(self):
        # Reinit attributes of the UI
        self.__reinit_ui()

        # Some aesthetic value
        size_btn = QtCore.QSize(180, 40)
        icon_size = QtCore.QSize(20, 20)
        btn_icon_size = QtCore.QSize(28, 28)

        # Main Layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        self.setLayout(main_layout)

        # Main Layout Child 1 : Folder path Layout
        layout_folder = QtWidgets.QHBoxLayout()
        main_layout.addLayout(layout_folder)
        # Main Layout Child : Texture plugged
        self.__ui_layout_textures = QtWidgets.QVBoxLayout()
        main_layout.addLayout(self.__ui_layout_textures)
        # Main Layout Child : Button Submit
        self.__ui_btn_submit = QtWidgets.QPushButton("Assign to the selection and close")
        self.__ui_btn_submit.setFixedSize(size_btn)
        main_layout.addWidget(self.__ui_btn_submit, 0, QtCore.Qt.AlignCenter)

        # Folder Path Layout
        self.__ui_folder = QtWidgets.QLineEdit()
        self.__ui_folder.setFixedHeight(btn_icon_size.height() + 3)
        self.__ui_btn_folder = QtWidgets.QPushButton()
        self.__ui_btn_folder.setIconSize(icon_size)
        self.__ui_btn_folder.setFixedSize(btn_icon_size)
        self.__ui_btn_folder.setIcon(
            QtGui.QIcon(QtGui.QPixmap("C:/Users/m.jenin/Documents/marius/shader_maker/assets/browse.png")))
        layout_folder.addWidget(self.__ui_folder)
        layout_folder.addWidget(self.__ui_btn_folder)

    def __populate_textures_plugged(self):
        onlyfiles = [f for f in listdir(self.__folder_path) if isfile(join(self.__folder_path, f))]
        print(onlyfiles)
        # TODO CREATE UI FOR TEXTURES PLUGGED


    def __browse_folder(self):
        folder_name = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")
        self.__ui_folder.setText(folder_name)

    def __on_folder_changed(self):
        folder_path_tmp = self.__ui_folder.text()
        if(os.path.isdir(folder_path_tmp)):
            self.__folder_path = folder_path_tmp
            self.__populate_textures_plugged()

    def __submit_assignment(self):
        self.__retrieve_selected()
        if self.is_valid_to_assign():
            self.__assign_to_selection()
            self.close()
        else:
            pass
            # TODO IF NO SELECTION

    # Link action to elements in the UI
    def __link_actions(self):
        self.__ui_btn_folder.clicked.connect(self.__browse_folder)
        self.__ui_folder.textChanged.connect(self.__on_folder_changed)
        self.__ui_btn_submit.clicked.connect(self.__submit_assignment)

    def __assign_to_selection(self):
        # TODO ASSIGN
        pass

    def print(self):
        print("selected_list ", end="")
        print(self.__selected_list)
        print("folder_path ", end="")
        print(self.__folder_path)
        print("texture_list ", end="")
        print(self.__texture_list)


if __name__ == '__main__':
    ltp = ShaderMaker()
    ltp.show()
    ltp.print()
