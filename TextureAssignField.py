
from abc import ABC, abstractmethod
import re


# Represents a Rule for a field in the shader
class AssignFieldRule:
    ValueCondition = True
    ExistanceCondition = False
    Greater = True
    Lesser = False
    Exist = True
    NotExist = False

    def __init__(self, regexp, type, rule):
        # Model attributes
        self.regexp = regexp
        self.type = type
        self.rule = rule

    # Compile the regexp
    def compile(self):
        re.compile(self.regexp)


# Represents a Field in the shader
class TextureAssignField(ABC):

    def __init__(self, shader, regexp, rules_1=None, rules_2=None):
        # Model attributes
        self.__ordered_matches = []
        self._shader = shader
        self._regexp = re.compile(regexp)
        rules_1 = [] if rules_1 is None else rules_1
        rules_2 = [] if rules_2 is None else rules_2
        for rule in rules_1:
            rule.compile()
        for rule in rules_2:
            rule.compile()
        self.rules_1 = rules_1
        self.rules_2 = rules_2


    @abstractmethod
    def assign(self, path_tex_name):
        pass

    # Compute the list of textures that correspond to the field oredred according to their relevance
    def compute_ordered_matches(self, tex_name_list):
        # Get all the files that match the main regex
        filtered_list = []
        for tex_name in tex_name_list:
            if re.match(self._regexp, tex_name):
                filtered_list.append(tex_name)


        # Sort the files according to the first set of rules
        length_pattern_order = len(self.rules_1)
        ordered_list = [[] for _ in range(length_pattern_order + 1)]
        index_ordered_list = 0
        for rule in self.rules_1:
            filtered_to_remove = []
            list_to_sort = [[] for _ in range(length_pattern_order + 1)]
            if rule.type:
                for tex_name in filtered_list:
                    if match := re.search(rule.regexp, tex_name, re.IGNORECASE):
                        list_to_sort[index_ordered_list].append([tex_name, match.group(1)])
                        filtered_to_remove.append(tex_name)
                list_to_sort[index_ordered_list].sort(key=lambda x: int(x[1]), reverse=not rule.type)
                for val in list_to_sort[index_ordered_list]:
                    ordered_list[index_ordered_list].append(val[0])
            else:
                for tex_name in filtered_list:
                    if (re.match(rule.regexp, tex_name) is not None) is rule.rule:
                        list_to_sort[index_ordered_list].append(tex_name)
                        filtered_to_remove.append(tex_name)
                for val in list_to_sort[index_ordered_list]:
                    ordered_list[index_ordered_list].append(val)

            for elem_to_remove in filtered_to_remove:
                filtered_list.remove(elem_to_remove)
            index_ordered_list += 1

        # Sort the files according to the second set of rules (keeping th priority from the first set)
        ordered_tested_list = []
        for rule in self.rules_2:
            if rule.type:
                list_to_sort = []
                for ordered_list_item in ordered_list:
                    list_to_remove = []
                    for tex_name in ordered_list_item:
                        if match := re.search(rule.regexp, tex_name, re.IGNORECASE):
                            list_to_sort.append([tex_name, match.group(1)])
                            list_to_remove.append(tex_name)
                    for elem_to_remove in list_to_remove:
                        ordered_list_item.remove(elem_to_remove)

                list_to_sort.sort(key=lambda x: int(x[1]), reverse=rule.rule)
                for val in list_to_sort:
                    ordered_tested_list.append(val[0])
            else:
                list_to_append = []
                for ordered_list_item in ordered_list:
                    list_to_remove = []
                    for tex_name in ordered_list_item:
                        if (re.match(rule.regexp, tex_name) is not None) is rule.rule:
                            list_to_append.append(tex_name)
                            list_to_remove.append(tex_name)
                    for elem_to_remove in list_to_remove:
                        ordered_list_item.remove(elem_to_remove)
                for val in list_to_append:
                    ordered_tested_list.append(val)

        for ordered_list_item in ordered_list:
            for tex_name in ordered_list_item:
                ordered_tested_list.append(tex_name)

        self.__ordered_matches = ordered_tested_list

    # Getter of the ordered matches
    def get_ordered_matches(self):
        return self.__ordered_matches


# Represents an Albedo field in the shader
class AlbedoTextureField(TextureAssignField):
    def __init__(self, shader):
        super().__init__(shader,
                         r".*(BaseColor|Albedo).*",
                         [
                             AssignFieldRule(r".*\.exr", AssignFieldRule.ExistanceCondition, AssignFieldRule.Exist),
                             AssignFieldRule(r".*\.jpg", AssignFieldRule.ExistanceCondition, AssignFieldRule.Exist),
                         ],
                         [
                             AssignFieldRule(r".*LOD[0-9].*", AssignFieldRule.ExistanceCondition,
                                             AssignFieldRule.NotExist),
                             AssignFieldRule(r".*LOD([0-9]).*", AssignFieldRule.ValueCondition, AssignFieldRule.Lesser)
                         ])

    def assign(self, path_tex_name):
        # TODO
        pass


# Represents a Normal field in the shader
class NormalTextureField(TextureAssignField):
    def __init__(self, shader):
        super().__init__(shader,
                         r".*(Normal).*",
                         [
                             AssignFieldRule(r".*\.exr", AssignFieldRule.ExistanceCondition, AssignFieldRule.Exist),
                             AssignFieldRule(r".*\.jpg", AssignFieldRule.ExistanceCondition, AssignFieldRule.Exist),
                         ],
                         [
                             AssignFieldRule(r".*LOD[0-9].*", AssignFieldRule.ExistanceCondition,
                                             AssignFieldRule.NotExist),
                             AssignFieldRule(r".*LOD([0-9]).*", AssignFieldRule.ValueCondition, AssignFieldRule.Lesser)
                         ])

    def assign(self, path_tex_name):
        # TODO
        pass


# Represents a Roughness field in the shader
class RoughnessTextureField(TextureAssignField):
    def __init__(self, shader):
        super().__init__(shader,
                         r".*(Roughness).*",
                         [
                             AssignFieldRule(r".*\.exr", AssignFieldRule.ExistanceCondition, AssignFieldRule.Exist),
                             AssignFieldRule(r".*\.jpg", AssignFieldRule.ExistanceCondition, AssignFieldRule.Exist),
                         ])

    def assign(self, path_tex_name):
        # TODO
        pass


# Represents a Translucency field in the shader
class TranslucencyTextureField(TextureAssignField):
    def __init__(self, shader):
        super().__init__(shader,
                         r".*(Translucency).*",
                         [
                             AssignFieldRule(r".*\.exr", AssignFieldRule.ExistanceCondition, AssignFieldRule.Exist),
                             AssignFieldRule(r".*\.jpg", AssignFieldRule.ExistanceCondition, AssignFieldRule.Exist),
                         ])

    def assign(self, path_tex_name):
        # TODO
        pass


# Represents an Opacity field in the shader
class OpacityTextureField(TextureAssignField):
    def __init__(self, shader):
        super().__init__(shader,
                         r".*(Opacity).*",
                         [
                             AssignFieldRule(r".*\.exr", AssignFieldRule.ExistanceCondition, AssignFieldRule.Exist),
                             AssignFieldRule(r".*\.jpg", AssignFieldRule.ExistanceCondition, AssignFieldRule.Exist),
                         ])

    def assign(self, path_tex_name):
        # TODO
        pass


# Represents a Metalness field in the shader
class MetalnessTextureField(TextureAssignField):
    def __init__(self, shader):
        super().__init__(shader,
                         r".*(Metalness).*",
                         [
                             AssignFieldRule(r".*\.exr", AssignFieldRule.ExistanceCondition, AssignFieldRule.Exist),
                             AssignFieldRule(r".*\.jpg", AssignFieldRule.ExistanceCondition, AssignFieldRule.Exist),
                         ])

    def assign(self, path_tex_name):
        # TODO
        pass


# Represents a Displacement field in the shader Substance
class DisplaceSubstanceTextureField(TextureAssignField):
    def __init__(self, shader):
        super().__init__(shader,
                         r".*(Height).*",
                         [
                             AssignFieldRule(r".*\.exr", AssignFieldRule.ExistanceCondition, AssignFieldRule.Exist),
                             AssignFieldRule(r".*\.jpg", AssignFieldRule.ExistanceCondition, AssignFieldRule.Exist),
                         ])

    def assign(self, path_tex_name):
        # TODO
        pass


# Represents a Displacement field in the shader Megascan3D
class DisplaceMegascan3DTextureField(TextureAssignField):
    def __init__(self, shader):
        super().__init__(shader,
                         r".*(Displacement).*",
                         [
                             AssignFieldRule(r".*\.exr", AssignFieldRule.ExistanceCondition, AssignFieldRule.Exist),
                             AssignFieldRule(r".*\.jpg", AssignFieldRule.ExistanceCondition, AssignFieldRule.Exist),
                         ])

    def assign(self, path_tex_name):
        # TODO
        pass


# Represents a Displacement field in the shader Megascan3DPlant
class DisplaceMegascan3DPlantTextureField(TextureAssignField):
    def __init__(self, shader):
        super().__init__(shader, r"(?!x)x", )

    def assign(self, path_tex_name):
        # TODO
        pass

# If Displace subdivide 2
