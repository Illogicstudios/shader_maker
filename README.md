# shader_maker

Shader Maker is a tool to automatically create shaders on Maya from Substance texture files.

## How to install

You must specify the correct path of the installation folder in the template_main.py file :
```python
if __name__ == '__main__':
    # TODO specify the right path
    install_dir = 'PATH/TO/shader_maker'
    # [...]
```
 
## Features
### Creation of shader

You can selects a folder with texture files or a parent folder of folders of texture files. The corresponding shaders are detected and can be assigned automatically by replacing shaders with the same name. A shader can also be assigned to selected objects.

### Update of shaders

You can change path of texture files connected to shaders of objects selected. You just have to select a new folder with the same texture file names.
