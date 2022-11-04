from abc import ABC
import os
from functools import partial
from os.path import isfile, join
import re

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

from TextureAssignField import AlbedoTextureField, NormalTextureField, RoughnessTextureField, MetalnessTextureField, \
    DisplaceSubstanceTextureField, DisplaceMegascan3DTextureField, DisplaceMegascan3DPlantTextureField, \
    OpacityTextureField, TranslucencyTextureField
from utils import clear_layout


# Field in the UI
class FieldShader:
    def __init__(self, title, texture_assign_field):
        # Model attibutes
        self.title = title
        self.tex_assign_field = texture_assign_field
        self.tex_name = None


# Represents the folder inspected with certain fields to fill with textures
class TextureFolderAssignShader(ABC):

    # Populate with a message in case of no texture retrieved
    @staticmethod
    def _populate_empty(main_layout_shader):
        clear_layout(main_layout_shader)
        main_layout_shader.addWidget(QtWidgets.QLabel("No textures found"), 0, QtCore.Qt.AlignCenter)

    # Browse a new texture for a specific field
    @staticmethod
    def __on_click_browse_texture(context_widget, widget_tex_name, folder_path):
        file_name = QtWidgets.QFileDialog.getOpenFileName(context_widget, "Select File", folder_path)
        if len(file_name[0]) > 0:
            widget_tex_name.setText(os.path.basename(file_name[0]))

    def __init__(self, shader):
        # Model attibutes
        self.__nb_col = 3
        self._folder_path = None
        self._tex_name_list = []
        self._shader = shader
        self._fields = []

    # Refresh the image when the texture name change
    def __on_change_texture_name(self, field, layout_img, tex_name):
        field.tex_name = tex_name if isfile(tex_name) else None
        self.__fill_with_image(tex_name, layout_img)

    # Fill the layout with the right image
    def __fill_with_image(self, tex_name, layout):
        side_image = int((650 - (self.__nb_col - 1) * 25) / self.__nb_col)
        clear_layout(layout)
        tex_path = os.path.dirname(self._folder_path + "/") + "/" + str(tex_name)
        widget_texture = QtWidgets.QLabel()
        # TODO replace by a loader of different types of image
        if tex_name is None:
            pixmap = QtGui.QPixmap("C:/Users/m.jenin/Documents/marius/shader_maker/assets/none.png")
        else:
            if tex_path[-3:] != "jpg":
                tex_path_jpg = tex_path[:-3] + "jpg"
                if isfile(tex_path_jpg):
                    pixmap = QtGui.QPixmap(tex_path_jpg)
                else:
                    pixmap = QtGui.QPixmap("C:/Users/m.jenin/Documents/marius/shader_maker/assets/no_texture.png")
            else:
                pixmap = QtGui.QPixmap(tex_path)

        widget_texture.setPixmap(pixmap.scaled(side_image, side_image, QtCore.Qt.KeepAspectRatio))
        layout.addWidget(widget_texture)

    # Populate the folder UI
    def populate(self, main_layout_shader, folder_path):
        # Populate with empty if no texture have been retrieved
        if self.is_empty():
            TextureFolderAssignShader._populate_empty(main_layout_shader)
            return False
        clear_layout(main_layout_shader)
        layout_shader = QtWidgets.QGridLayout()

        # Scroll Area
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll_area_widget = QtWidgets.QWidget()
        scroll_area.setWidget(scroll_area_widget)
        scroll_area_widget.setLayout(layout_shader)

        # Some aesthetic value
        icon_size = QtCore.QSize(18, 18)
        btn_icon_size = QtCore.QSize(24, 24)

        # Populate with a card for each field
        index_col = 0
        index_row = 0
        for shader_field_pair in self._fields:
            layout_shader_field = QtWidgets.QVBoxLayout()
            layout_shader_field.setMargin(5)
            frame_shader_field = QtWidgets.QFrame()
            frame_shader_field.setLayout(layout_shader_field)
            frame_shader_field.setFrameShape(QtWidgets.QFrame.StyledPanel)
            frame_shader_field.setFrameShadow(QtWidgets.QFrame.Plain)

            title = shader_field_pair.title
            tex_name = shader_field_pair.tex_name

            # Label Title
            widget_title = QtWidgets.QLabel(title)
            widget_title.setFont(QtGui.QFont('MS Sans Serif', 10))
            widget_title.setStyleSheet("font-weight:bold")
            widget_title.setMargin(5)
            widget_title.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
            layout_shader_field.addWidget(widget_title)

            # Image
            layout_image = QtWidgets.QVBoxLayout()
            self.__fill_with_image(tex_name, layout_image)
            layout_shader_field.addLayout(layout_image)

            # Label Texture Name
            layout_tex_name = QtWidgets.QHBoxLayout()
            widget_tex_name = QtWidgets.QLineEdit(tex_name)
            layout_tex_name.addWidget(widget_tex_name)
            widget_tex_name.textChanged.connect(partial(self.__on_change_texture_name, shader_field_pair, layout_image))
            widget_tex_name.setFixedHeight(btn_icon_size.height() + 3)
            browse_btn = QtWidgets.QPushButton()
            browse_btn.setIconSize(icon_size)
            browse_btn.setFixedSize(btn_icon_size)
            browse_btn.setIcon(QtGui.QIcon(
                QtGui.QPixmap("C:/Users/m.jenin/Documents/marius/shader_maker/assets/browse.png")))  # TODO REMOVE

            browse_btn.clicked.connect(partial(TextureFolderAssignShader.__on_click_browse_texture,
                                               frame_shader_field, widget_tex_name, folder_path))
            layout_tex_name.addWidget(browse_btn)
            layout_shader_field.addLayout(layout_tex_name)

            layout_shader.addWidget(frame_shader_field, index_row, index_col)
            if index_col == self.__nb_col - 1:
                index_col = 0
                index_row += 1
            else:
                index_col += 1

        main_layout_shader.addWidget(scroll_area)
        return True

    # Setter of the folder_path
    def set_folder_path(self, folder_path):
        self._folder_path = folder_path

    # Reinitialize the fields to None
    def reinit_fields(self):
        for field in self._fields:
            field.tex_name = None

    # Getter of whether the fields are all at None are not
    def is_empty(self):
        for field in self._fields:
            if field.tex_name is not None:
                return False
        return True

    # Assign the right tex_name to each field
    def assign_to_fields(self):
        fields_pref = []
        for field in self._fields:
            fields_pref.append((0, field.tex_assign_field.get_ordered_matches()))

        for i in range(len(self._fields)):
            index_match = 0

            ordered_matches_curr = fields_pref[i][1]
            self._fields[i].tex_name = ordered_matches_curr[index_match] if index_match < len(
                ordered_matches_curr) else None

        for field in self._fields:
            field.tex_assign_field.assign(
                None if field.tex_name is None else os.path.dirname(self._folder_path + "/") + "/" + str(
                    field.tex_name))

    # Retrieve the texture in the folder
    def find_tex_into_folder(self):
        self._tex_name_list = [f for f in os.listdir(self._folder_path) if
                               isfile(join(self._folder_path, f)) and re.match(r".*\.[exr|jpg]", f)]
        for field in self._fields:
            field.tex_assign_field.compute_ordered_matches(self._tex_name_list)


# Folder for a Substance Asset
class SubstanceTextureFolderAssignShader(TextureFolderAssignShader):
    def __init__(self, shader):
        super().__init__(shader)
        self._fields = [
            FieldShader("Albedo", AlbedoTextureField(self._shader)),
            FieldShader("Normal", NormalTextureField(self._shader)),
            FieldShader("Displace", DisplaceSubstanceTextureField(self._shader)),
            FieldShader("Roughness", RoughnessTextureField(self._shader)),
            FieldShader("Metalness", MetalnessTextureField(self._shader)),
        ]


# Folder for a Megascan3D Asset
class Megascan3DTextureFolderAssignShader(TextureFolderAssignShader):
    def __init__(self, shader):
        super().__init__(shader)
        self._fields = [
            FieldShader("Albedo", AlbedoTextureField(self._shader)),
            FieldShader("Normal", NormalTextureField(self._shader)),
            FieldShader("Displacement", DisplaceMegascan3DTextureField(self._shader)),
            FieldShader("Roughness", RoughnessTextureField(self._shader)),
            FieldShader("Metalness", MetalnessTextureField(self._shader)),
        ]


# Folder for a Megascan3DPlant Asset
class Megascan3DPlantTextureFolderAssignShader(TextureFolderAssignShader):
    def __init__(self, shader):
        super().__init__(shader)
        self._fields = [
            FieldShader("Albedo", AlbedoTextureField(self._shader)),
            FieldShader("Normal", NormalTextureField(self._shader)),
            FieldShader("Displacement", DisplaceMegascan3DPlantTextureField(self._shader)),
            FieldShader("Roughness", RoughnessTextureField(self._shader)),
            FieldShader("Metalness", MetalnessTextureField(self._shader)),
            FieldShader("Opacity", OpacityTextureField(self._shader)),
            FieldShader("Translucency", TranslucencyTextureField(self._shader)),
        ]
