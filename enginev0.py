# a.py
#
# Single-file Ursina/Panda3D configuration for macOS (including M1) and
# an example of loading "marioshead" from SM64. You must provide your
# own legally obtained model and texture. This script references:
#   - marioshead.obj (model)
#   - marioshead_diffuse.png (texture)
#
# Place them in the same folder or adjust paths accordingly.

##################################
# 1) Panda3D engine configuration
##################################
from panda3d.core import loadPrcFileData

# Set window title (optional)
loadPrcFileData('', 'window-title SM64 Mario Head')

# Force OpenGL 4.1 core profile (useful on macOS)
loadPrcFileData('', 'gl-version 4 1')

# Required for modern GL usage
loadPrcFileData('', 'gl-force-fbo true')

# Optionally skip OpenGL error checks for performance
loadPrcFileData('', 'gl-check-errors false')

# (Optional) If you need multi-threaded rendering:
# loadPrcFileData('', 'threading-model Cull/Draw')

# (Optional) Enable PStats performance monitoring
# loadPrcFileData('', 'want-pstats true')
# loadPrcFileData('', 'pstats-python-profiler true')

# (Optional) For debugging OpenGL calls:
# loadPrcFileData('', 'notify-level-glgsg debug')

##################################
# 2) Ursina imports and setup
##################################
from ursina import *
import platform, sys, time

app = Ursina(vsync=True, development_mode=False)

# macOS fix for locked cursor in FirstPerson-like views:
if platform.system() == 'Darwin':
    window.set_cursor_hidden(True)

##################################
# 3) Load the Mario Head model
##################################
# Provide your own "marioshead.obj" and "marioshead_diffuse.png"
# If they are named differently, update the lines below.

try:
    marioshead = Entity(model='marioshead.obj', 
                        texture='marioshead_diffuse.png', 
                        scale=1.0)
    marioshead.position = (0, 0, 0)
except Exception as e:
    print("Failed to load marioshead model:", e)
    # Fallback to a simple cube if Mario’s head is not available
    marioshead = Entity(model='cube', color=color.yellow, scale=1.0)
    marioshead.position = (0, 0, 0)

##################################
# 4) (Optional) Custom shader
##################################
# You can apply a custom GLSL shader if you want to override default shading.
# If you just want the default unlit texturing, skip this section.

vertex_shader_code = """
#version 410 core
// Basic vertex shader
uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 vertex;
in vec2 uv;
out vec2 uv_coord;
void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * vertex;
    uv_coord = uv;
}
"""

fragment_shader_code = """
#version 410 core
// Basic fragment shader (sample a texture)
uniform sampler2D p3d_Texture0;
in vec2 uv_coord;
out vec4 frag_color;
void main() {
    frag_color = texture(p3d_Texture0, uv_coord);
}
"""

try:
    marioshead.shader = Shader(
        language=Shader.GLSL,
        vertex=vertex_shader_code,
        fragment=fragment_shader_code
    )
except Exception as err:
    print("Shader compilation error:", err)
    marioshead.shader = None  # Revert to default if shader fails

# If you want collision on the model (for raycasting, clicks, etc.)
marioshead.collider = 'mesh'

##################################
# 5) Lighting setup (optional)
##################################
# Ursina uses an unlit shader by default. For “lit” shading with a custom
# shader, you must handle lights yourself. Below is an example directional light.
directional_light = DirectionalLight(shadows=True)
directional_light.look_at(marioshead)
directional_light.color = color.white
light_entity = Entity(light=directional_light, 
                      rotation=(45, -45, 45))  # adjust rotation as needed

##################################
# 6) Input handling
##################################
def input(key):
    if key == 'escape':
        application.quit()
    elif key == 'r':
        # Reset rotation of Mario's head
        marioshead.rotation = (0,0,0)
    elif key == 'f':
        # Toggle wireframe mode
        marioshead.wireframe = not marioshead.wireframe

##################################
# 7) Update loop
##################################
def update():
    # Example: rotate Mario’s head 10 degrees per second around Y-axis
    marioshead.rotation_y += 10 * time.dt

# Enable FPS counter
window.fps_counter.enabled = True

##################################
# 8) Run the application
##################################
app.run()
