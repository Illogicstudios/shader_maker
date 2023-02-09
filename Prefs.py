import json
import os
import ctypes
import sys

# ######################################################################################################################

_FOLDER_PREFS = ".illogic_prefs"
_COMMON_FILE = "common"

# ######################################################################################################################


class PrefsNotInitialized(Exception):
    # Raised when the prefs file doesn't exist
    pass


class Prefs:
    def __init__(self, file_name=_COMMON_FILE):
        if type(file_name) != str:
            raise TypeError("Project name must be a string")

        path_home = os.path.expanduser("~")
        self.__path_prefs = path_home + "/" + _FOLDER_PREFS
        self.__file_path = self.__path_prefs + "/" + file_name

    def __create_folder_prefs(self):
        if not os.path.exists(self.__path_prefs):
            os.makedirs(self.__path_prefs)
            ctypes.windll.kernel32.SetFileAttributesW(self.__path_prefs, 0x02)

    def __create_project_file(self):
        if not os.path.exists(self.__file_path):
            f = open(self.__file_path, "x")
            f.close()

    def __get_datas(self):
        f = open(self.__file_path, "r")
        content = f.read()
        f.close()

        if len(content) == 0:
            datas = {}
        else:
            datas = json.loads(content)
        return datas

    def __contains__(self, item):
        if not os.path.exists(self.__file_path):
            return False
        return item in self.__get_datas()

    def __getitem__(self, index):
        index = str(index)
        if not os.path.exists(self.__file_path):
            raise IndexError(index + " doesn't exists in prefs")
        datas = self.__get_datas()
        if not index in datas:
            raise IndexError(index + " doesn't exists in prefs")
        return self.__get_datas()[index]

    def __setitem__(self, index, item):
        self.__create_folder_prefs()
        self.__create_project_file()

        f = open(self.__file_path, "r+")
        content = f.read()
        if len(content) == 0:
            datas = {}
        else:
            datas = json.loads(content)
        datas[str(index)] = item
        f.seek(0)
        f.truncate()
        f.write(json.dumps(datas, indent=1))
        f.close()

    def pop(self, index):
        self.__create_folder_prefs()
        self.__create_project_file()

        f = open(self.__file_path, "r+")

        content = f.read()
        if len(content) == 0:
            datas = {}
        else:
            datas = json.loads(content)

        item = None
        if index in datas:
            item = datas.pop(index)
            f.seek(0)
            f.truncate()
            f.write(json.dumps(datas, indent=1))
        f.close()
        return item
