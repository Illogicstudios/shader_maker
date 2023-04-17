from os.path import isfile, join

import ShaderMaker
from ShaderMaker import *

from IdealFlowLayout import IdealFlowLayout

########################################################################################################################

SHADER_FIELDS = {
    "Base Color": {
        "rule": r"(.*)(?:basecolor|albedo|diffuse).*\.(?:" + ShaderMaker.FILE_EXTENSION_SUPPORTED_REGEX + ")",
        "color_enabled": (86, 216, 121), "color_disabled": (19, 51, 28)
    },
    "Normal": {
        "rule": r"((?:(?!combine).)*)(?:normal)(?:(?!combine).)*\.(?:" + ShaderMaker.FILE_EXTENSION_SUPPORTED_REGEX + ")",
        "color_enabled": (128, 128, 255), "color_disabled": (32, 32, 64)
    },
    "Displacement": {
        "rule": r"(.*)(?:height|displacement|disp).*\.(?:" + ShaderMaker.FILE_EXTENSION_SUPPORTED_REGEX + ")",
        "color_enabled": (243, 112, 112), "color_disabled": (54, 25, 25)
    },
    "Roughness": {
        "rule": r"(.*)(?:roughness).*\.(?:" + ShaderMaker.FILE_EXTENSION_SUPPORTED_REGEX + ")",
        "color_enabled": (152, 104, 223), "color_disabled": (35, 22, 52)
    },
    "Metalness": {
        "rule": r"(.*)(?:metalness).*\.(?:" + ShaderMaker.FILE_EXTENSION_SUPPORTED_REGEX + ")",
        "color_enabled": (189, 231, 231), "color_disabled": (54, 66, 66)
    },
    "Emissive": {
        "rule": r"(.*)(?:emissive).*\.(?:" + ShaderMaker.FILE_EXTENSION_SUPPORTED_REGEX + ")",
        "color_enabled": (247, 247, 108), "color_disabled": (51, 51, 21)
    },
    "SSS Amount": {
        "rule": r"(.*)(?:sssamount).*\.(?:" + ShaderMaker.FILE_EXTENSION_SUPPORTED_REGEX + ")",
        "color_enabled": (231, 164, 121), "color_disabled": (78, 54, 39)
    },
}


########################################################################################################################


# A Texture field in the shader
class ShaderField:
    def __init__(self, rule, color_enabled, color_disabled):
        self.__regexp = rule
        self.__file_name = ""
        self.__color_enabled = color_enabled
        self.__color_disabled = color_disabled
        self.__enabled = True
        self.__btn = None

    def set_btn(self, btn):
        self.__btn = btn

    def get_file_name(self):
        return self.__file_name

    def set_file_name(self, file_name):
        self.__file_name = file_name

    def get_regexp(self):
        return self.__regexp

    def is_found(self):
        return len(self.__file_name) > 0

    def is_enabled(self):
        return self.__enabled

    def set_enabled(self, enabled):
        self.__enabled = enabled
        self.refresh_btn()

    def toggle_enabled(self):
        self.__enabled = not self.__enabled
        self.refresh_btn()

    def refresh_btn(self):
        if self.__btn is not None:
            if self.__enabled:
                color = self.__color_enabled
                color_text = "black"
            else:
                color = self.__color_disabled
                color_text = "gray"

            self.__btn.setStyleSheet("background-color:rgb(" + str(color[0]) + "," + str(color[1]) + "," + str(
                color[2]) + ");color:" + color_text)


class Shader:
    ALL_SHADER_ENABLED_CHECKBOX = QtWidgets.QCheckBox()
    ALL_SHADER_ENABLED_CHECKBOX.setChecked(True)
    ALL_FIELD_STATE = {k: {"enabled": True, "btn": QtWidgets.QPushButton(k)} for k in SHADER_FIELDS.keys()}

    @staticmethod
    def __header_enabled_changed(shader_maker, checked):
        shader_maker.set_all_shaders_enabled(checked)

    @staticmethod
    def __header_field_btn_changed(shader_maker, keyword):
        Shader.ALL_FIELD_STATE[keyword]["enabled"] = not Shader.ALL_FIELD_STATE[keyword]["enabled"]
        shader_maker.set_all_field_enabled(keyword, Shader.ALL_FIELD_STATE[keyword]["enabled"])
        Shader.refresh_header_btn(keyword, Shader.ALL_FIELD_STATE[keyword]["btn"])

    @staticmethod
    def refresh_header_btn(keyword, btn):
        if Shader.ALL_FIELD_STATE[keyword]["enabled"]:
            color = SHADER_FIELDS[keyword]["color_enabled"]
            color_text = "black"
        else:
            color = SHADER_FIELDS[keyword]["color_disabled"]
            color_text = "gray"

        btn.setStyleSheet("background-color:rgb(" + str(color[0]) + "," + str(color[1]) + "," + str(
            color[2]) + ");color:" + color_text)

    @staticmethod
    def generate_header(shader_maker, lyt):
        shader_card = QtWidgets.QHBoxLayout()
        shader_card.setContentsMargins(9, 5, 9, 5)
        shader_card.setSpacing(5)
        frame_shader_card = QtWidgets.QFrame()
        frame_shader_card.setStyleSheet("background-color:rgb(45,45,45)")
        frame_shader_card.setLayout(shader_card)
        frame_shader_card.setFrameShape(QtWidgets.QFrame.StyledPanel)
        frame_shader_card.setFrameShadow(QtWidgets.QFrame.Plain)

        enabled_checkbox = Shader.ALL_SHADER_ENABLED_CHECKBOX
        enabled_checkbox.setChecked(True)
        enabled_checkbox.stateChanged.connect(partial(Shader.__header_enabled_changed, shader_maker))
        enabled_checkbox.setFixedSize(enabled_checkbox.sizeHint())
        shader_card.addWidget(enabled_checkbox)

        all_label = QtWidgets.QLabel("All shaders")
        all_label.setAlignment(QtCore.Qt.AlignCenter)
        all_label.setFixedWidth(150)
        shader_card.addWidget(all_label)

        flow_layout = IdealFlowLayout()
        flow_layout.setSpacing(0)
        flow_layout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        for keyword, data in SHADER_FIELDS.items():
            btn = Shader.ALL_FIELD_STATE[keyword]["btn"]
            btn.setFixedSize(QtCore.QSize(btn.sizeHint().width(), btn.sizeHint().height()))
            btn.clicked.connect(partial(Shader.__header_field_btn_changed, shader_maker, keyword))
            Shader.refresh_header_btn(keyword, btn)
            flow_layout.addWidget(btn)
        shader_card.addLayout(flow_layout)

        lyt.addWidget(frame_shader_card)

    def __init__(self, title):
        self.__shader_fields = {}
        for keyword, fields_info in SHADER_FIELDS.items():
            self.__shader_fields[keyword] = ShaderField(fields_info["rule"],
                                                        fields_info["color_enabled"], fields_info["color_disabled"])
        self.__title = title
        self.__dir_path = ""
        self.__ui_checkbox = None
        self.__image_label = None
        self.__enabled = Shader.ALL_SHADER_ENABLED_CHECKBOX.isChecked()

    # Getter of the title
    def get_title(self):
        return self.__title

    def set_field_enabled(self, keyword, enabled):
        self.__shader_fields[keyword].set_enabled(enabled)

    def set_enabled(self, enabled):
        self.__enabled = enabled
        self.__refresh_checkbox()

    def __refresh_checkbox(self):
        self.__ui_checkbox.setChecked(self.__enabled)

    # Load the field according to the folder
    def load(self, folder_path):
        # Get all the texture files of the folder
        files_name_list = [f for f in os.listdir(folder_path) if
                           isfile(join(folder_path, f)) and re.match(
                               r".*\.(?:" + ShaderMaker.FILE_EXTENSION_SUPPORTED_REGEX + ")", f, re.IGNORECASE)]
        files_name_list.sort(key=str)
        files_name_list.reverse()
        # Sort and store objects according to their prefix to detect if many shaders are in the folder
        field_file_match = {}
        for keyword, field in self.__shader_fields.items():
            regexp = field.get_regexp()
            for file_name in files_name_list:
                match = re.match(regexp, file_name.lower(), re.IGNORECASE)
                if match:
                    prefix = match.groups()[0]
                    if prefix not in field_file_match:
                        field_file_match[prefix] = {keyword: []}
                    elif keyword not in field_file_match[prefix]:
                        field_file_match[prefix][keyword] = []
                    field_file_match[prefix][keyword].append(file_name)

        nb_file_field_match = len(field_file_match)
        # If many shaders, create as much shaders
        if nb_file_field_match > 1:
            shaders = []
            for prefix, field_datas in field_file_match.items():
                prefix_to_title = prefix[:-1] if prefix[-1] == "_" else prefix
                shader = Shader(prefix_to_title)
                shader.__dir_path = folder_path
                for keyword, file_names in field_datas.items():
                    shader.__shader_fields[keyword].set_file_name(folder_path + "/" + file_names[0])
                shaders.append((shader, len(field_datas)))
            return shaders
        # If only one shader keep the current one
        elif nb_file_field_match == 1:
            self.__dir_path = os.path.dirname(folder_path)
            prefix = list(field_file_match.keys())[0]
            prefix = prefix[:-1] if prefix[-1] == "_" else prefix
            self.__title = prefix if self.__title[0].isdigit() else self.__title
            shader_val = list(field_file_match.values())[0]
            for keyword, file_names in shader_val.items():
                self.__shader_fields[keyword].set_file_name(folder_path + "/" + file_names[0])
            return [(self, len(shader_val))]
        return []

    # Populate the ui with the data of the shader
    def populate(self, shader_maker, lyt):
        shader_card = QtWidgets.QHBoxLayout()
        shader_card.setContentsMargins(5, 5, 5, 5)
        shader_card.setSpacing(5)
        frame_shader_card = QtWidgets.QFrame()
        frame_shader_card.setLayout(shader_card)
        frame_shader_card.setFrameShape(QtWidgets.QFrame.StyledPanel)
        frame_shader_card.setFrameShadow(QtWidgets.QFrame.Plain)

        self.__ui_checkbox = QtWidgets.QCheckBox()
        self.__refresh_checkbox()
        self.__ui_checkbox.stateChanged.connect(partial(self.__enabled_changed, shader_maker))
        self.__ui_checkbox.setFixedSize(self.__ui_checkbox.sizeHint())
        shader_card.addWidget(self.__ui_checkbox)

        shader_title = QtWidgets.QLineEdit(self.__title)
        shader_title.setReadOnly(True)
        shader_title.setFixedWidth(150)
        shader_card.addWidget(shader_title)

        flow_layout = IdealFlowLayout()
        flow_layout.setSpacing(0)
        flow_layout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        for keyword, field in self.__shader_fields.items():
            if field.is_found():
                btn = QtWidgets.QPushButton(keyword)
                field.set_btn(btn)
                btn.setFixedSize(QtCore.QSize(btn.sizeHint().width(), btn.sizeHint().height()))
                btn.clicked.connect(partial(field.toggle_enabled))
                btn.setToolTip(os.path.basename(field.get_file_name()))
                field.set_enabled(Shader.ALL_FIELD_STATE[keyword]["enabled"])
                field.refresh_btn()
                flow_layout.addWidget(btn)
        shader_card.addLayout(flow_layout)

        lyt.addWidget(frame_shader_card)

    def __enabled_changed(self, shader_maker, checked):
        self.__enabled = checked == QtCore.Qt.Checked
        shader_maker.refresh_btn()

    def is_enabled(self):
        return self.__enabled

    def __generate_base_color(self, in_tex, out_tex):
        field = self.__shader_fields["Base Color"]
        if field.is_found() and field.is_enabled():
            base_color_file_name = self.__shader_fields["Base Color"].get_file_name()
            base_color = pm.shadingNode("file", asTexture=True, name="Base Color")
            base_color.fileTextureName.set(base_color_file_name)
            base_color.uvTilingMode.set(3)
            in_tex.outUV >> base_color.uvCoord
            base_color.outColor >> out_tex.baseColor
            base_color.outColor >> out_tex.subsurfaceColor

    def __generate_roughness(self, in_tex, out_tex):
        field = self.__shader_fields["Roughness"]
        if field.is_found() and field.is_enabled():
            roughness_file_name = self.__shader_fields["Roughness"].get_file_name()
            roughness = pm.shadingNode("file", asTexture=True, name="Roughness")
            roughness.fileTextureName.set(roughness_file_name)
            roughness.uvTilingMode.set(3)
            remap_value = pm.shadingNode("remapValue", asUtility=True, name="remapValue")
            in_tex.outUV >> roughness.uvCoord
            roughness.outColorR >> remap_value.inputValue
            remap_value.outValue >> out_tex.specularRoughness

    def __generate_normal(self, in_tex, out_tex):
        field = self.__shader_fields["Normal"]
        if field.is_found() and field.is_enabled():
            normal_file_name = self.__shader_fields["Normal"].get_file_name()
            normal = pm.shadingNode("file", asTexture=True, name="Normal")
            normal.fileTextureName.set(normal_file_name)
            normal.uvTilingMode.set(3)
            normal_map = pm.shadingNode("aiNormalMap", asUtility=True, name="aiNormalMap")
            in_tex.outUV >> normal.uvCoord
            normal.outColor >> normal_map.input
            normal_map.outValue >> out_tex.normalCamera

    def __generate_metalness(self, in_tex, out_tex):
        field = self.__shader_fields["Metalness"]
        if field.is_found() and field.is_enabled():
            metalness_file_name = self.__shader_fields["Metalness"].get_file_name()
            metalness = pm.shadingNode("file", asTexture=True, name="Metalness")
            metalness.fileTextureName.set(metalness_file_name)
            metalness.uvTilingMode.set(3)
            in_tex.outUV >> metalness.uvCoord
            metalness.outColorR >> out_tex.metalness

    def __generate_displacement(self, in_tex, displacement_scale, displacement_mid):
        displacement_node = None
        field = self.__shader_fields["Displacement"]
        if field.is_found() and field.is_enabled():
            height_file_name = self.__shader_fields["Displacement"].get_file_name()
            height = pm.shadingNode("file", asTexture=True, name="Displacement")
            height.fileTextureName.set(height_file_name)
            height.uvTilingMode.set(3)
            displacement_node = pm.shadingNode("displacementShader", asUtility=True, name="displacementShader")
            displacement_node.scale.set(displacement_scale)
            displacement_node.aiDisplacementZeroValue.set(displacement_mid)
            in_tex.outUV >> height.uvCoord
            height.outColorR >> displacement_node.displacement
        return displacement_node

    def __generate_sss_amount(self, in_tex, out_tex):
        field = self.__shader_fields["SSS Amount"]
        if field.is_found() and field.is_enabled():
            sss_amount_file_name = self.__shader_fields["SSS Amount"].get_file_name()
            sss_amount = pm.shadingNode("file", asTexture=True, name="SSS Amount")
            sss_amount.fileTextureName.set(sss_amount_file_name)
            sss_amount.uvTilingMode.set(3)
            remap_value = pm.shadingNode("remapValue", asUtility=True, name="remapValue")
            in_tex.outUV >> sss_amount.uvCoord
            sss_amount.outColorR >> remap_value.inputValue
            remap_value.outValue >> out_tex.subsurface

    def __generate_emissive(self, in_tex, out_tex):
        field = self.__shader_fields["Emissive"]
        if field.is_found() and field.is_enabled():
            emissive_file_name = self.__shader_fields["Emissive"].get_file_name()
            emissive = pm.shadingNode("file", asTexture=True, name="Emissive")
            emissive.fileTextureName.set(emissive_file_name)
            emissive.uvTilingMode.set(3)
            remap_color = pm.shadingNode("remapColor", asUtility=True, name="remapColor")
            in_tex.outUV >> emissive.uvCoord
            emissive.outColor >> remap_color.color
            remap_color.outColor >> out_tex.emissionColor

    # Generate the shader according to the data of the shader
    def generate_shading_nodes(self, values):
        place_texture = pm.shadingNode("place2dTexture", asUtility=True, name="place2dTexture")

        arnold_node = pm.shadingNode("aiStandardSurface", asShader=True, name=self.__title)

        self.__generate_base_color(place_texture, arnold_node)
        self.__generate_roughness(place_texture, arnold_node)
        self.__generate_metalness(place_texture, arnold_node)
        self.__generate_normal(place_texture, arnold_node)
        displacement_node = self.__generate_displacement(place_texture, values["displacement_scale"],
                                                         values["displacement_mid"])
        self.__generate_sss_amount(place_texture, arnold_node)
        self.__generate_emissive(place_texture, arnold_node)

        return {arnold_node, displacement_node}
