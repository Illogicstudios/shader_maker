import sys

if __name__ == '__main__':
    # TODO specify the right path
    install_dir = 'PATH/TO/shader_maker'
    if not sys.path.__contains__(install_dir):
        sys.path.append(install_dir)

    import ShaderMaker
    from ShaderMaker import *

    unload_packages(silent=True, packages=["ShaderMaker", "Shader", "IdealFlowLayout"])
    ltp = ShaderMaker()
    ltp.show()
