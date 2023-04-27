import importlib
from common import utils

utils.unload_packages(silent=True, package="shader_maker")
importlib.import_module("shader_maker")
from shader_maker.ShaderMaker import ShaderMaker
try:
    shader_maker.close()
except:
    pass
shader_maker = ShaderMaker()
shader_maker.show()
