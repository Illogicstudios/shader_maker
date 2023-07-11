from os.path import isfile, join

import shader_maker.ShaderMaker as ShaderMaker
from .ShaderMaker import *

########################################################################################################################

SHADER_FIELDS_REGEX = {
    "base_color": r"(.*)(?:basecolor|albedo|diffuse).*\.(?:" + ShaderMaker.FILE_EXTENSION_SUPPORTED_REGEX + ")",
    "normal": r"((?:(?!combine).)*)(?:normal)(?:(?!combine).)*\.(?:" + ShaderMaker.FILE_EXTENSION_SUPPORTED_REGEX + ")",
    "displacement": r"(.*)(?:height|displacement|disp).*\.(?:" + ShaderMaker.FILE_EXTENSION_SUPPORTED_REGEX + ")",
    "roughness": r"(.*)(?:roughness).*\.(?:" + ShaderMaker.FILE_EXTENSION_SUPPORTED_REGEX + ")",
    "metalness": r"(.*)(?:metalness).*\.(?:" + ShaderMaker.FILE_EXTENSION_SUPPORTED_REGEX + ")",
    "emissive": r"(.*)(?:emissive).*\.(?:" + ShaderMaker.FILE_EXTENSION_SUPPORTED_REGEX + ")",
    "sss": r"(.*)(?:sssamount).*\.(?:" + ShaderMaker.FILE_EXTENSION_SUPPORTED_REGEX + ")"
}


########################################################################################################################


class ShaderField:
    """
    A Texture field in the shader
    """
    def __init__(self, rule):
        """
        :param rule: regexp that valid the ShaderField
        """
        self.__regexp = rule
        self.__file_name = ""
        self.__enabled = True

    def get_file_name(self):
        """
        Getter of the filename
        :return: filename
        """
        return self.__file_name

    def set_file_name(self, file_name):
        """
        Setter of the filename
        :param file_name
        :return:
        """
        self.__file_name = file_name

    def get_regexp(self):
        """
        Getter of the regexp
        :return: regexp
        """
        return self.__regexp

    def is_found(self):
        """
        Getter of whether the ShaderField has been found or not
        :return: boolean
        """
        return len(self.__file_name) > 0

    def is_enabled(self):
        """
        Getter of whether the ShaderField is enabled or not
        :return: boolean
        """
        return self.__enabled

    def set_enabled(self, enabled):
        """
        Setter of the enabled field
        :param enabled
        :return:
        """
        self.__enabled = enabled

    def toggle_enabled(self):
        """
        Toggle the enabled field
        :return:
        """
        self.__enabled = not self.__enabled


class Shader:
    def __init__(self, title):
        """
        Constructor
        :param title:
        """
        self.__shader_fields = {}
        for keyword, rule in SHADER_FIELDS_REGEX.items():
            self.__shader_fields[keyword] = ShaderField(rule)
        self.__title = title
        self.__dir_path = ""
        self.__image_label = None

    def get_title(self):
        """
        Getter of the title
        :return: title
        """
        return self.__title

    def set_field_enabled(self, keyword, enabled):
        """
        Setter of the enable field of a keyword
        :param keyword
        :param enabled
        :return:
        """
        self.__shader_fields[keyword].set_enabled(enabled)

    def load(self, folder_path):
        """
        Load the field according to the folder
        :param folder_path:
        :return:
        """
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

    def get_field(self, keyword):
        """
        Getter of a field of the shader
        :param keyword
        :return: shader_field
        """
        return self.__shader_fields[keyword]

    def __generate_base_color(self, in_tex, out_tex):
        """
        Generate the base color
        :param in_tex: input texture
        :param out_tex: output texture
        :return:
        """
        field = self.__shader_fields["base_color"]
        if field.is_found() and field.is_enabled():
            base_color_file_name = field.get_file_name()
            base_color = pm.shadingNode("file", asTexture=True, name="Base Color")
            base_color.fileTextureName.set(base_color_file_name)
            base_color.uvTilingMode.set(3)
            in_tex.outUV >> base_color.uvCoord
            base_color.outColor >> out_tex.baseColor
            base_color.outColor >> out_tex.subsurfaceColor

    def __generate_roughness(self, in_tex, out_tex):
        """
        Generate the roughness
        :param in_tex: input texture
        :param out_tex: output texture
        :return:
        """
        field = self.__shader_fields["roughness"]
        if field.is_found() and field.is_enabled():
            roughness_file_name = field.get_file_name()
            roughness = pm.shadingNode("file", asTexture=True, name="Roughness")
            roughness.fileTextureName.set(roughness_file_name)
            roughness.uvTilingMode.set(3)
            remap_value = pm.shadingNode("remapValue", asUtility=True, name="remapValue")
            in_tex.outUV >> roughness.uvCoord
            roughness.outColorR >> remap_value.inputValue
            remap_value.outValue >> out_tex.specularRoughness

    def __generate_normal(self, in_tex, out_tex):
        """
        Generate the normal
        :param in_tex: input texture
        :param out_tex: output texture
        :return:
        """
        field = self.__shader_fields["normal"]
        if field.is_found() and field.is_enabled():
            normal_file_name = field.get_file_name()
            normal = pm.shadingNode("file", asTexture=True, name="Normal")
            normal.fileTextureName.set(normal_file_name)
            normal.uvTilingMode.set(3)
            normal_map = pm.shadingNode("aiNormalMap", asUtility=True, name="aiNormalMap")
            in_tex.outUV >> normal.uvCoord
            normal.outColor >> normal_map.input
            normal_map.outValue >> out_tex.normalCamera

    def __generate_metalness(self, in_tex, out_tex):
        """
        Generate the metalness
        :param in_tex: input texture
        :param out_tex: output texture
        :return:
        """
        field = self.__shader_fields["metalness"]
        if field.is_found() and field.is_enabled():
            metalness_file_name = field.get_file_name()
            metalness = pm.shadingNode("file", asTexture=True, name="Metalness")
            metalness.fileTextureName.set(metalness_file_name)
            metalness.uvTilingMode.set(3)
            in_tex.outUV >> metalness.uvCoord
            metalness.outColorR >> out_tex.metalness

    def __generate_displacement(self, in_tex, displacement_scale, displacement_mid):
        """
        Generate the displacement
        :param in_tex: input texture
        :param displacement_scale
        :param displacement_mid
        :return: displacement node
        """
        displacement_node = None
        field = self.__shader_fields["displacement"]
        if field.is_found() and field.is_enabled():
            height_file_name = field.get_file_name()
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
        """
        Generate the sss
        :param in_tex: input texture
        :param out_tex: output texture
        :return:
        """
        field = self.__shader_fields["sss"]
        if field.is_found() and field.is_enabled():
            sss_amount_file_name = field.get_file_name()
            sss_amount = pm.shadingNode("file", asTexture=True, name="SSS Amount")
            sss_amount.fileTextureName.set(sss_amount_file_name)
            sss_amount.uvTilingMode.set(3)
            remap_value = pm.shadingNode("remapValue", asUtility=True, name="remapValue")
            in_tex.outUV >> sss_amount.uvCoord
            sss_amount.outColorR >> remap_value.inputValue
            remap_value.outValue >> out_tex.subsurface

    def __generate_emissive(self, in_tex, out_tex):
        """
        Generate the emissive
        :param in_tex: input texture
        :param out_tex: output texture
        :return:
        """
        field = self.__shader_fields["emissive"]
        if field.is_found() and field.is_enabled():
            emissive_file_name = field.get_file_name()
            emissive = pm.shadingNode("file", asTexture=True, name="Emissive")
            emissive.fileTextureName.set(emissive_file_name)
            emissive.uvTilingMode.set(3)
            remap_color = pm.shadingNode("remapColor", asUtility=True, name="remapColor")
            in_tex.outUV >> emissive.uvCoord
            emissive.outColor >> remap_color.color
            remap_color.outColor >> out_tex.emissionColor

    # Generate the shader according to the data of the shader
    def generate_shading_nodes(self, values):
        """
        Generate all the shader graph
        :param values: shader values
        :return: arnold node and displacement node
        """
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
