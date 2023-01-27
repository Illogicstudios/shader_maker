# Shader Maker

Shader Maker is a tool to create Arnold shaders faster and to update textures easily.

## How to install

You must specify the correct path of the installation folder in the template_main.py file :
```python
if __name__ == '__main__':
    # TODO specify the right path
    install_dir = 'PATH/TO/shader_maker'
    # [...]
```
 
## Features

### Create Shader Part

Select or type either :
- a folder of texture files to load one shader in the interface
- a folder of folders of texture files to load many shaders in the interface

The corresponding shader(s) are displayed in the below area. 

You can spcify which Displacement Scale and Mid to use in this area.

Click the Create Shader Button to submit the shaders that you want to create.

You can select one of the three options :

- Replace by shader name : It will scan the scene to find shader with the same name. This allows you to replace temporary shaders named in the same way. If no shaders is found the behavior is the same as the No assignation option.

- Assign to selection : It will assign the shader loaded to the objects selected in the scene (This option is enabled only when 1 shader is selected). If no object is found the behavior is the same as the No assignation option.

- No assignation : The shaders created are attached to temporary spheres.

Check boxes can be clicked to select or not a shader for the assignation

### Update Texture Part

Select or type a folder of new versions of texture files and select objects in the scene which have textures to update.

Files for which a new version is found are displayed in white and the files for which a match has not been found are displayed in gray

Click the Update Shader Button to overrides the files which a new version is foundSelect objects in the scene which have textures to update
