# Import Ursina engine and relevant classes
from ursina import Ursina, Entity, color, Vec3, window, time, invoke, camera
from ursina.shaders import lit_with_shadows_shader  # Shader for dynamic lighting/shadows&#8203;:contentReference[oaicite:2]{index=2}
from ursina.lights import DirectionalLight, AmbientLight
import math

# Initialize the Ursina app and window
app = Ursina() 
window.title = "Mario64 Head - Ursina Engine"    # Window title
window.color = color.black                      # Black background (like SM64 title screen)
window.fps_counter.enabled = False              # Hide FPS counter for a cleaner view

# Define some colors for Mario
skin_color = color.rgb(254, 209, 176)   # Peach skin tone (Mario’s face)
hat_color  = color.rgb(238, 28, 37)     # Mario’s hat red color
hair_color = color.rgb(30, 20, 10)      # Dark brown (for hair or mustache, using near-black)

# Create a parent entity for Mario's head (all parts will be children of this)
mario = Entity(name='MarioHead')

# Create head (base) as a sphere
head = Entity(parent=mario, model='sphere', color=skin_color, scale=1.0, 
              shader=lit_with_shadows_shader)

# Create Mario's nose as a smaller sphere, positioned in front of the face
nose = Entity(parent=mario, model='sphere', color=skin_color, scale=0.25, 
              position=(0, 0.0, 0.5), shader=lit_with_shadows_shader)
nose_original_scale = nose.scale  # store original scale for animations

# Create ears as small spheres on the sides of the head
ear_left  = Entity(parent=mario, model='sphere', color=skin_color, scale=0.2, 
                   position=(0.5, 0.0, 0.0), shader=lit_with_shadows_shader)
ear_right = Entity(parent=mario, model='sphere', color=skin_color, scale=0.2, 
                   position=(-0.5, 0.0, 0.0), shader=lit_with_shadows_shader)

# Create eyes using white spheres (eyeballs) and black pupils
eye_left = Entity(parent=mario, model='sphere', color=color.white, scale=0.15, 
                  position=(0.15, 0.1, 0.5), shader=lit_with_shadows_shader)
eye_right = Entity(parent=mario, model='sphere', color=color.white, scale=0.15, 
                   position=(-0.15, 0.1, 0.5), shader=lit_with_shadows_shader)
# Pupils as tiny black spheres slightly in front of the eyeballs
pupil_left = Entity(parent=eye_left, model='sphere', color=color.black, scale=0.05, 
                    position=(0, 0, 0.1), shader=lit_with_shadows_shader)
pupil_right = Entity(parent=eye_right, model='sphere', color=color.black, scale=0.05, 
                     position=(0, 0, 0.1), shader=lit_with_shadows_shader)

# Create hat: top part as a flattened sphere, and brim as a flattened cube
hat_top = Entity(parent=mario, model='sphere', color=hat_color, shader=lit_with_shadows_shader,
                 scale=(1.2, 0.5, 1.2), position=(0, 0.3, 0))    # slightly above head, squashed vertically
# Hat brim as a flat rectangular slab in front of the head
hat_brim = Entity(parent=mario, model='cube', color=hat_color, shader=lit_with_shadows_shader,
                  scale=(0.8, 0.1, 0.3), position=(0, 0.2, 0.35))
hat_brim.rotation_x = 20  # tilt the brim downward a bit for style

# Create a simple mustache using a few small black spheres
moustache_center = Entity(parent=mario, model='sphere', color=color.black, shader=lit_with_shadows_shader,
                          scale=0.1, position=(0, -0.15, 0.45))
moustache_left   = Entity(parent=mario, model='sphere', color=color.black, shader=lit_with_shadows_shader,
                          scale=0.1, position=(0.15, -0.15, 0.43))
moustache_right  = Entity(parent=mario, model='sphere', color=color.black, shader=lit_with_shadows_shader,
                          scale=0.1, position=(-0.15, -0.15, 0.43))

# (Optional) Performance optimization: If individual part animation wasn’t needed, 
# we could combine all child models into one mesh for fewer draw calls:
# mario.combine()  # combine children into mario's mesh (improves performance&#8203;:contentReference[oaicite:3]{index=3})
# (We skip this here to allow part-by-part animation like nose stretching.)

# Set up lighting – a directional light for key lighting and an ambient light for fill
sun = DirectionalLight(shadows=True, color=color.white)  # main light (with shadows enabled)
sun.position = Vec3(2, 2, -2)      # place light above and in front of Mario
sun.look_at(mario)                # point the light toward the model&#8203;:contentReference[oaicite:4]{index=4}

ambient = AmbientLight(color=color.rgb(64, 64, 64))  # soft ambient light to brighten shadows

# Position the camera to view the head clearly
camera.position = (0, 0, -3)    # move camera a bit back along -Z to fit the head in view
camera.look_at(mario)           # ensure camera points at the model
# (Using Ursina's default perspective camera; we could also enable EditorCamera() for free movement)

# Animation variables for idle motion
angle = 0
stretch_timer = 0

def update():
    """Update is called every frame to animate the scene."""
    global angle, stretch_timer
    # Idle animation: slight oscillating rotation (like a slow head shake)
    angle += time.dt
    mario.rotation_y = math.sin(angle * 0.5) * 5  # rotate left-right by ±5 degrees
    
    # Periodically stretch the nose as a fun effect
    stretch_timer += time.dt
    if stretch_timer > 5:  # every 5 seconds
        # Animate nose scaling (make it 1.5x bigger, then back to original)
        nose.animate_scale(nose_original_scale * 1.5, duration=0.2)
        invoke(nose.animate_scale, nose_original_scale, duration=0.2, delay=0.3)
        stretch_timer = 0

# You can also trigger the nose stretch manually by pressing the "s" key:
def input(key):
    if key == 's':
        nose.animate_scale(nose_original_scale * 1.5, duration=0.2)
        invoke(nose.animate_scale, nose_original_scale, duration=0.2, delay=0.3)

# Run the Ursina app (opens the window and starts the rendering loop)
app.run()
