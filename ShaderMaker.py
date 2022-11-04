import os
from functools import partial

import maya.cmds as cmds
import maya.OpenMayaUI as omui

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

from shiboken2 import wrapInstance

from TextureFolderAssignShader import SubstanceTextureFolderAssignShader, Megascan3DTextureFolderAssignShader, \
    Megascan3DPlantTextureFolderAssignShader


class ShaderMaker(QtWidgets.QDialog):

    def __init__(self, parent=wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)):
        super(ShaderMaker, self).__init__(parent)

        # Model attributes
        self.__selected_list = []
        self.__folder_path = None
        self.__shader = None  # TODO init shader
        self.__texture_folder = SubstanceTextureFolderAssignShader(self.__shader)

        # UI attributes
        self.__reinit_ui()

        # name the window
        self.setWindowTitle("Shader Maker")
        # make the window a "tool" in Maya's eyes so that it stays on top when you click off
        self.setWindowFlags(QtCore.Qt.Tool)
        # Makes the object get deleted from memory, not just hidden, when it is closed.
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # Create the layout, linking it to actions and refresh the display
        self.__create_layout()
        self.__link_actions()
        self.__populate_textures_plugged()
        self.__refresh_btn()

    # Do we have an object to assign the shader to
    def is_valid_to_assign(self):
        return len(self.__selected_list) > 0

    # Retrieve the selected object in maya
    def __retrieve_selected(self):
        self.__selected_list = cmds.ls(sl=True, dag=True)

    # Reinitialize the ui in order to repopulate it
    def __reinit_ui(self):
        self.__ui_folder = None
        self.__ui_layout_shader_fields = None
        self.__ui_dropdown_shader_plug_list = []
        self.__ui_btn_folder = None
        self.__ui_btn_submit = None

    # Refresh the state of buttons
    def __refresh_btn(self):
        self.__ui_btn_submit.setEnabled(not self.__texture_folder.is_empty())

    # Change type of asset (change field to fill)
    def __change_type_asset(self, folder_type, enabled):
        if enabled:
            self.__texture_folder = folder_type(self.__shader)
            self.__populate_textures_plugged()

    # Create the layout
    def __create_layout(self):
        # Reinit attributes of the UI
        self.__reinit_ui()
        self.setFixedSize(720, 780)
        self.move(QtWidgets.QDesktopWidget().availableGeometry().center() - self.frameGeometry().center())

        # Some aesthetic value
        size_btn = QtCore.QSize(250, 40)
        icon_size = QtCore.QSize(20, 20)
        btn_icon_size = QtCore.QSize(28, 28)

        # Main Layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(10, 15, 10, 10)
        main_layout.setSpacing(20)
        self.setLayout(main_layout)

        # Main Layout Child 1 : Group Button Choose Type asset
        layout_asset_type = QtWidgets.QHBoxLayout()
        main_layout.addLayout(layout_asset_type)
        # Main Layout Child 2 : Folder path Layout
        layout_folder = QtWidgets.QHBoxLayout()
        main_layout.addLayout(layout_folder)
        # Main Layout Child 3 : Texture plugged
        self.__ui_layout_shader_fields = QtWidgets.QVBoxLayout()
        main_layout.addLayout(self.__ui_layout_shader_fields)
        # Main Layout Child 4 : Button Submit
        layout_btn_submit = QtWidgets.QVBoxLayout()
        layout_btn_submit.setMargin(5)
        main_layout.addLayout(layout_btn_submit)

        # Group Button Choose Type asset
        button_group_asset_type = QtWidgets.QButtonGroup()
        substance_type_btn = QtWidgets.QRadioButton('Substance', self)
        substance_type_btn.toggled.connect(
            partial(self.__change_type_asset, SubstanceTextureFolderAssignShader))
        megascan_3d_type_btn = QtWidgets.QRadioButton('Megascan 3D', self)
        megascan_3d_type_btn.toggled.connect(
            partial(self.__change_type_asset, Megascan3DTextureFolderAssignShader))
        megascan_3d_plant_type_btn = QtWidgets.QRadioButton('Megascan 3D Plant', self)
        megascan_3d_plant_type_btn.toggled.connect(
            partial(self.__change_type_asset, Megascan3DPlantTextureFolderAssignShader))
        button_group_asset_type.addButton(substance_type_btn)
        button_group_asset_type.addButton(megascan_3d_type_btn)
        button_group_asset_type.addButton(megascan_3d_plant_type_btn)
        layout_asset_type.addWidget(substance_type_btn, 0, QtCore.Qt.AlignRight)
        layout_asset_type.addWidget(megascan_3d_type_btn, 0, QtCore.Qt.AlignHCenter)
        layout_asset_type.addWidget(megascan_3d_plant_type_btn, 0, QtCore.Qt.AlignLeft)

        # Folder Path Layout
        self.__ui_folder = QtWidgets.QLineEdit()
        self.__ui_folder.setFixedHeight(btn_icon_size.height() + 3)
        self.__ui_btn_folder = QtWidgets.QPushButton()
        self.__ui_btn_folder.setIconSize(icon_size)
        self.__ui_btn_folder.setFixedSize(btn_icon_size)
        self.__ui_btn_folder.setIcon(QtGui.QIcon(
            QtGui.QPixmap("C:/Users/m.jenin/Documents/marius/shader_maker/assets/browse.png")))  # TODO REMOVE
        layout_folder.addWidget(self.__ui_folder)
        layout_folder.addWidget(self.__ui_btn_folder)

        # Button Submit
        self.__ui_btn_submit = QtWidgets.QPushButton("Assign to the selection and close")
        self.__ui_btn_submit.setFixedSize(size_btn)
        self.__ui_btn_submit.setStyleSheet("QPushButton{padding: 25px;}")
        self.__ui_btn_submit.setEnabled(False)
        layout_btn_submit.addWidget(self.__ui_btn_submit, 0, QtCore.Qt.AlignHCenter)

        substance_type_btn.toggle()

    # Populate the UI according to the folder and the texture plugged
    def __populate_textures_plugged(self):
        if self.__folder_path is not None:
            self.__texture_folder.set_folder_path(self.__folder_path)
            self.__texture_folder.find_tex_into_folder()
            self.__texture_folder.assign_to_fields()
        self.__texture_folder.populate(self.__ui_layout_shader_fields, self.__folder_path)

    # Find a new folder to inspect
    def __browse_folder(self):
        folder_name = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory",
                                                                 "R:/megascan/Downloaded/3d")  # TODO remove
        if len(folder_name) > 0:
            self.__ui_folder.setText(folder_name)

    # Refresh UI and model attribute when folder changes
    def __on_folder_changed(self):
        folder_path_tmp = self.__ui_folder.text()
        if os.path.isdir(folder_path_tmp):
            self.__folder_path = folder_path_tmp
        else:
            self.__folder_path = None
            self.__texture_folder.reinit_fields()
        self.__populate_textures_plugged()
        self.__refresh_btn()

    # Validate the shader set up and create and assign it
    def __submit_assignment(self):
        self.__retrieve_selected()
        if self.is_valid_to_assign():
            self.__validate_shader()
            self.close()
        else:
            print("No selection")

    # Link action to elements in the UI
    def __link_actions(self):
        self.__ui_btn_folder.clicked.connect(self.__browse_folder)
        self.__ui_folder.textChanged.connect(self.__on_folder_changed)
        self.__ui_btn_submit.clicked.connect(self.__submit_assignment)

    # Assign the shader to the selection
    def __validate_shader(self):
        # TODO ASSIGN
        pass


if __name__ == '__main__':
    ltp = ShaderMaker()
    ltp.show()
