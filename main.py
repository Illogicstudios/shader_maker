import sys

# TODO CHANGE PATH
dir = 'C:/Users/m.jenin/Documents/marius/shader_maker'
if not sys.path.__contains__(dir):
    sys.path.append('C:/Users/m.jenin/Documents/marius/shader_maker')

# if you have some packages that you often reload, you can put them here
# and they will get reloaded if "packages" attribute is not explicitly stated
DEFAULT_RELOAD_PACKAGES = []


def unload_packages(silent=True, packages=None):
    if packages is None:
        packages = DEFAULT_RELOAD_PACKAGES

    # construct reload list
    reload_list = []
    for i in sys.modules.keys():
        for package in packages:
            if i.startswith(package):
                reload_list.append(i)

    # unload everything
    for i in reload_list:
        try:
            if sys.modules[i] is not None:
                del (sys.modules[i])
                if not silent:
                    print("Unloaded: %s" % i)
        except:
            pass


from ShaderMaker import ShaderMaker

if __name__ == '__main__':
    unload_packages(silent=True, packages=["ShaderMaker", "Shader"])
    ltp = ShaderMaker()
    ltp.show()
