# test.py - Procedurally render the Super Mario 64 Render96 title in Ursina

# === 1. Engine and Graphics Configuration (for macOS M1 OpenGL 4.1 core) ===
from panda3d.core import loadPrcFileData
# Force OpenGL 4.1 core profile (required for advanced OpenGL on macOS M1)&#8203;:contentReference[oaicite:6]{index=6}
loadPrcFileData('', 'gl-version 4 1')        # Request OpenGL 4.1 context
# (Optional performance tweaks: e.g., disable vsync or enable certain Panda3D optimizations if needed)

from ursina import Ursina, Mesh, Entity, Shader, color, window, camera

# === 2. Initialize Ursina app ===
app = Ursina()
window.title = "Render96 Title Demo"        # Window title
window.fps_counter.enabled = True          # Enable FPS counter display&#8203;:contentReference[oaicite:7]{index=7}
# window.exit_button.visible = False       # (Optional) Hide window close button if not needed

# === 3. Define the geometry for each letter of "MARIO64" procedurally ===
# We represent letters as a set of filled grid cells (for a 5-unit tall grid).
# Each tuple: (width, height, set_of_filled_cells). Coordinate origin at bottom-left of letter.
letters = {
    'M': (5, 5, {   # M: fill left & right columns and a bottom-center block
        (0,0),(0,1),(0,2),(0,3),(0,4),     # left column
        (4,0),(4,1),(4,2),(4,3),(4,4),     # right column
        (2,0)                              # bottom middle tip of M
    }),
    'A': (4, 5, {   # A: fill left & right columns, top row, and a middle bar
        (0,0),(0,1),(0,2),(0,3),(0,4),     # left column
        (3,0),(3,1),(3,2),(3,3),(3,4),     # right column
        (0,4),(1,4),(2,4),(3,4),           # top row
        (1,2),(2,2)                        # middle crossbar
    }),
    'R': (4, 5, {   # R: like P (left col + two top rows) plus a diagonal block for leg
        (0,0),(0,1),(0,2),(0,3),(0,4),     # left column
        (1,4),(2,4),(3,4),                 # top row
        (1,3),(2,3),(3,3),                 # second row below top
        (1,1)                              # extra block for the leg of R
    }),
    'I': (3, 5, {   # I: use a 3-wide grid; fill top row, bottom row, and middle column
        (0,4),(1,4),(2,4),                 # top bar
        (1,3),(1,2),(1,1),                 # middle column
        (0,0),(1,0),(2,0)                  # bottom bar
    }),
    'O': (4, 5, {   # O: fill the border of a 4x5 rectangle (hollow center)
        (0,0),(1,0),(2,0),(3,0),           # bottom row
        (0,1),(0,2),(0,3),                 # left column (interior part)
        (3,1),(3,2),(3,3),                 # right column (interior part)
        (0,4),(1,4),(2,4),(3,4)            # top row
        # (Center (1,1),(2,1),(1,2),(2,2),(1,3),(2,3) are empty, creating a hole)
    }),
    '6': (4, 5, {   # 6: fill like O but open the top-right to resemble '6'
        (0,0),(1,0),(2,0),(3,0),           # bottom
        (0,1),(0,2),(0,3),(0,4),           # left column
        (1,2),(2,2),(3,2),                 # middle bar
        (1,4),(2,4),                       # top (left part)
        (3,0),(3,1),(3,2)                  # right column (bottom half)
    }),
    '4': (4, 5, {   # 4: vertical right bar + horizontal mid bar + top left part
        (3,0),(3,1),(3,2),(3,3),(3,4),     # right column
        (0,3),(0,4),                       # top left part
        (1,2),(2,2),(3,2)                  # middle bar
    })
}

# Colors for each letter (approximate Mario 64 logo colors)
letter_colors = {
    'M': color.red,        # red
    'A': color.orange,     # orange
    'R': color.yellow,     # yellow
    'I': color.green,      # green
    'O': color.azure,      # blue (azure used as light blue)
    '6': color.violet,     # purple/violet
    '4': color.cyan        # cyan/light-blue
}

# Now procedurally generate the mesh data (vertices, triangles, normals, colors)
vertices = []
triangles = []
normals = []
colors = []

# We will build all letters combined, with a small gap between them.
text = "MARIO64"
# Calculate total width for centering
total_width = 0
for ch in text:
    total_width += letters[ch][0]
    if ch != text[-1]:
        total_width += 1  # gap of 1 unit between letters

# Starting offset so that the whole text is centered at x=0
offset_x = -total_width / 2.0
current_x = offset_x

# Helper to add a face (two triangles) given four corner vertex indices
def add_face(v0, v1, v2, v3, normal_vec):
    """Add two triangles (v0,v1,v2) and (v0,v2,v3) with a given normal."""
    start_index = len(vertices)
    # Add vertices with the same normal
    vertices.extend([v0, v1, v2, v3])
    normals.extend([normal_vec, normal_vec, normal_vec, normal_vec])
    # Use the base color for all four vertices
    # (Color will be appended outside this function for clarity in code below)
    # Define triangles (using the indices 0,1,2,3 relative to this face's start_index)
    triangles.extend([
        start_index + 0, start_index + 1, start_index + 2,
        start_index + 0, start_index + 2, start_index + 3
    ])

# Loop through each letter and construct its faces
for ch in text:
    w, h, filled_cells = letters[ch]
    base_col = letter_colors.get(ch, color.white)
    # Iterate through each filled cell of the letter
    for (cx, cy) in filled_cells:
        # Calculate the 3D coordinates of the cell's corners on the front (z=0) and back (z=depth)
        # Front-face (toward camera) corners:
        x0 = current_x + cx
        x1 = current_x + cx + 1
        y0 = cy
        y1 = cy + 1
        z_front = 0.0
        z_back  = 0.5  # depth/thickness of letters
        # Corner positions
        top_left_front     = (x0, y1, z_front)
        bottom_left_front  = (x0, y0, z_front)
        bottom_right_front = (x1, y0, z_front)
        top_right_front    = (x1, y1, z_front)
        top_left_back      = (x0, y1, z_back)
        bottom_left_back   = (x0, y0, z_back)
        bottom_right_back  = (x1, y0, z_back)
        top_right_back     = (x1, y1, z_back)

        # Front face (facing camera, normal points -Z outward)
        add_face(top_left_front, bottom_left_front, bottom_right_front, top_right_front, normal_vec=(0,0,-1))
        # Back face (facing away from camera, normal +Z)
        add_face(bottom_left_back, top_left_back, top_right_back, bottom_right_back, normal_vec=(0,0,1))
        # Left face (if no neighbor to the left of this cell)
        if (cx-1, cy) not in filled_cells:
            add_face(top_left_back, bottom_left_back, bottom_left_front, top_left_front, normal_vec=(-1,0,0))
        # Right face
        if (cx+1, cy) not in filled_cells:
            add_face(bottom_right_back, top_right_back, top_right_front, bottom_right_front, normal_vec=(1,0,0))
        # Bottom face
        if (cx, cy-1) not in filled_cells:
            add_face(bottom_left_front, bottom_left_back, bottom_right_back, bottom_right_front, normal_vec=(0,-1,0))
        # Top face
        if (cx, cy+1) not in filled_cells:
            add_face(top_left_back, top_left_front, top_right_front, top_right_back, normal_vec=(0,1,0))
        # Assign color to the last added vertices (the ones we just added for all faces of this cell)
        # Each face added 4 vertices; we added 6 faces max (front, back, left, right, bottom, top).
        # To simplify, we'll append the base color for any new vertex added after adding faces.
        new_vertices_count = len(vertices) - len(colors)
        colors.extend([base_col] * new_vertices_count)
    # Move the current x position to start of next letter (including a 1 unit gap)
    current_x += w + 1

# Create the Ursina Mesh from the generated data
title_mesh = Mesh(
    vertices=vertices,
    triangles=triangles,
    normals=normals,
    colors=colors,
    static=True  # hint that geometry is not going to change (optimization)
)

# === 4. Define the custom GLSL shader for lighting (vertex and fragment) ===
vertex_shader_code = """
#version 330 core
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat3 p3d_NormalMatrix;
in vec3 vertex;
in vec3 normal;
in vec4 color;
out vec3 v_normal;
out vec3 v_position_view;
out vec4 v_color;
void main() {
    // Transform vertex to clip space
    gl_Position = p3d_ModelViewProjectionMatrix * vec4(vertex, 1.0);
    // Pass transformed normal and position to fragment shader
    v_normal = p3d_NormalMatrix * normal;
    v_position_view = (p3d_ModelViewMatrix * vec4(vertex, 1.0)).xyz;
    // Pass through the vertex color
    v_color = color;
}
"""

fragment_shader_code = """
#version 330 core
uniform vec3 light_dir;      // Direction from fragment to light (world or view space, normalized)
uniform vec3 light_color;
uniform vec3 ambient_color;
uniform vec3 spec_color;
uniform float shininess;
uniform vec4 p3d_ColorScale;
in vec3 v_normal;
in vec3 v_position_view;
in vec4 v_color;
out vec4 fragColor;
void main() {
    // Normalize the interpolated normal and light direction
    vec3 N = normalize(v_normal);
    vec3 L = normalize(light_dir);
    // Compute diffuse lighting (Lambertian)
    float diff = max(dot(N, L), 0.0);
    // Compute view direction (from fragment to camera). Camera is at origin in view space:
    vec3 V = normalize(-v_position_view);
    // Compute specular highlight (Blinn-Phong or Phong reflection)
    // Using Phong reflection: reflect the *incoming* light (negative of L since L is frag->light)
    vec3 R = reflect(-L, N);
    float spec_factor = 0.0;
    if(diff > 0.0) {
        spec_factor = pow(max(dot(V, R), 0.0), shininess);
    }
    vec3 diffuse = light_color * diff;
    vec3 specular = spec_color * spec_factor;
    vec3 ambient = ambient_color;
    // Combine lighting components and apply vertex color and entity color scale
    vec3 lit_color = (ambient + diffuse + specular) * v_color.rgb * p3d_ColorScale.rgb;
    fragColor = vec4(lit_color, v_color.a * p3d_ColorScale.a);
}
"""

# Create the Shader object
custom_shader = Shader(language=Shader.GLSL, vertex=vertex_shader_code, fragment=fragment_shader_code)

# === 5. Create the Entity for the title using our mesh and shader ===
title_entity = Entity(model=title_mesh, shader=custom_shader)

# Set up the shader inputs for lighting (these values can be tweaked for different effects)
# Directional light: pointing from above and left, towards the title.
# We provide the direction vector from surface to light.
light_direction = (-0.2, 0.8, -0.3)  # e.g., light coming from top-left-front
# Normalize the light direction vector
from math import sqrt
Lx,Ly,Lz = light_direction
length = sqrt(Lx*Lx + Ly*Ly + Lz*Lz)
light_dir_norm = (Lx/length, Ly/length, Lz/length)
# Send uniform inputs to the shader for all relevant entities (the title in this case)
title_entity.set_shader_input("light_dir", light_dir_norm)
title_entity.set_shader_input("light_color", (1.0, 1.0, 1.0))    # white light
title_entity.set_shader_input("ambient_color", (0.2, 0.2, 0.2))  # dim white ambient
title_entity.set_shader_input("spec_color", (1.0, 1.0, 1.0))     # white specular highlight
title_entity.set_shader_input("shininess", 64)                   # specular shininess factor

# === 6. Position the camera and lighting ===
# In this example, we manually position the camera to frame the title.
camera.position = (0, 2, -30)           # move camera back so entire title is visible
camera.look_at((0, 2, 0))              # point camera at the center of the title

# (No explicit DirectionalLight entity used since we pass light to shader directly)

# === 7. Run the app ===
app.run()
