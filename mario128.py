import pygame
import sys
import numpy as np
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# --- Initialization ---

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)

# Screen dimensions
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height), DOUBLEBUF | OPENGL)
pygame.display.set_caption("Mario-ish 3D (Mario 128 Style)")

# --- OpenGL Setup ---

def init_opengl():
    glClearColor(0.0, 0.0, 0.0, 1.0)  # Black background
    glEnable(GL_DEPTH_TEST)           # Enable depth testing (for 3D)
    glShadeModel(GL_SMOOTH)           # Smooth shading

    # Lighting (basic setup for now)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (0, 1, 1, 0))  # Directional light from above
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.8, 0.8, 1.0))

    # Perspective projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (screen_width / screen_height), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)

init_opengl()

# --- Colors (as before, but we'll use them with OpenGL) ---
black = (0, 0, 0)
white = (1, 1, 1)
blue = (0, 0, 1)
red = (1, 0, 0)
green = (0, 1, 0)
yellow = (1, 1, 0)

# --- Player ---

player_x = 0
player_y = 1  # Start slightly above the ground
player_z = -5
player_width = 0.5
player_height = 0.8
player_depth = 0.5
player_speed = 0.2
player_y_speed = 0
gravity = -0.02
jump_force = 0.5
is_jumping = False
grounded = True


def draw_player():
    glPushMatrix()
    glTranslatef(player_x, player_y, player_z)
    glColor3fv(blue)
    # Simple cube representation (you can make this more complex)
    draw_cube(player_width, player_height, player_depth)
    glPopMatrix()

# --- Camera ---
camera_x = 0
camera_y = 5
camera_z = 5
camera_target_x = 0
camera_target_y = 0
camera_target_z = -5
camera_up_x = 0
camera_up_y = 1
camera_up_z = 0

def set_camera():
    glLoadIdentity()
    gluLookAt(camera_x, camera_y, camera_z,  # Eye position
              camera_target_x, camera_target_y, camera_target_z,  # Look-at point
              camera_up_x, camera_up_y, camera_up_z)   # Up direction

# --- Ground ---

ground_y = 0
ground_size = 10

def draw_ground():
    glPushMatrix()
    glTranslatef(0, ground_y, -5)  # Move ground back a bit
    glColor3fv(green)
    glBegin(GL_QUADS)
    glVertex3f(-ground_size, 0, -ground_size)
    glVertex3f( ground_size, 0, -ground_size)
    glVertex3f( ground_size, 0,  ground_size)
    glVertex3f(-ground_size, 0,  ground_size)
    glEnd()
    glPopMatrix()

# --- Platforms ---

platforms = [
    (-2, 1, -8, 2, 0.5, 1),  # x, y, z, width, height, depth
    (2, 2, -12, 3, 0.5, 1.5),
    (0, 3, -18, 1, 0.5, 1),
]

def draw_platforms():
    glColor3fv(white)
    for platform in platforms:
        x, y, z, w, h, d = platform
        glPushMatrix()
        glTranslatef(x, y, z)
        draw_cube(w, h, d)
        glPopMatrix()

# --- Coins ---

coins = [
    (-2, 2, -8),  # x, y, z
    (2, 3, -12),
    (0, 4, -18),
]
collected_coins = 0

def draw_coins():
    glColor3fv(yellow)
    for i, coin in enumerate(coins):
        x, y, z = coin
        glPushMatrix()
        glTranslatef(x, y, z)
        draw_sphere(0.3)  # Small spheres
        glPopMatrix()

# --- Sound Generation (Same as before) ---

def create_n64_sound(frequency, duration, volume=0.5, attack=0.01, decay=0.1, sustain=0.5, release=0.1):
    sample_rate = 44100
    num_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, num_samples, False)
    wave1 = np.sign(np.sin(2 * np.pi * frequency * t))
    wave2 = np.arcsin(np.sin(2 * np.pi * frequency * 2 * t)) / (np.pi / 2)
    wave = 0.7 * wave1 + 0.3 * wave2
    attack_samples = int(sample_rate * attack)
    decay_samples = int(sample_rate * decay)
    sustain_level = sustain
    release_samples = int(sample_rate * release)
    envelope = np.ones(num_samples)
    envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    envelope[attack_samples:attack_samples + decay_samples] = np.linspace(1, sustain_level, decay_samples)
    release_start = num_samples - release_samples
    envelope[release_start:] = np.linspace(sustain_level, 0, release_samples)
    wave = (wave * envelope * 32767 * volume).astype(np.int16)
    return pygame.mixer.Sound(wave)

jump_sound = create_n64_sound(350, 0.2, volume=0.6, attack=0.01, decay=0.05, sustain=0.3, release=0.05)
wahoo_sound = create_n64_sound(440, 0.4, volume=0.8, attack=0.02, decay=0.1, sustain=0.6, release=0.2)
coin_sound = create_n64_sound(550, 0.1, volume=0.7, attack=0.005, decay=0.02, sustain=0.2, release=0.02)

# --- Score ---

font = pygame.font.Font(None, 36)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

# --- Helper Functions for 3D Drawing ---

def draw_cube(width, height, depth):
    half_width = width / 2
    half_height = height / 2
    half_depth = depth / 2

    glBegin(GL_QUADS)
    # Front face
    glNormal3f(0.0, 0.0, 1.0)
    glVertex3f(-half_width, -half_height, half_depth)
    glVertex3f( half_width, -half_height, half_depth)
    glVertex3f( half_width,  half_height, half_depth)
    glVertex3f(-half_width,  half_height, half_depth)

    # Back face
    glNormal3f(0.0, 0.0, -1.0)
    glVertex3f(-half_width, -half_height, -half_depth)
    glVertex3f(-half_width,  half_height, -half_depth)
    glVertex3f( half_width,  half_height, -half_depth)
    glVertex3f( half_width, -half_height, -half_depth)

    # Top face
    glNormal3f(0.0, 1.0, 0.0)
    glVertex3f(-half_width,  half_height, -half_depth)
    glVertex3f(-half_width,  half_height,  half_depth)
    glVertex3f( half_width,  half_height,  half_depth)
    glVertex3f( half_width,  half_height, -half_depth)

    # Bottom face
    glNormal3f(0.0, -1.0, 0.0)
    glVertex3f(-half_width, -half_height, -half_depth)
    glVertex3f( half_width, -half_height, -half_depth)
    glVertex3f( half_width, -half_height,  half_depth)
    glVertex3f(-half_width, -half_height,  half_depth)

    # Right face
    glNormal3f(1.0, 0.0, 0.0)
    glVertex3f( half_width, -half_height, -half_depth)
    glVertex3f( half_width,  half_height, -half_depth)
    glVertex3f( half_width,  half_height,  half_depth)
    glVertex3f( half_width, -half_height,  half_depth)

    # Left face
    glNormal3f(-1.0, 0.0, 0.0)
    glVertex3f(-half_width, -half_height, -half_depth)
    glVertex3f(-half_width, -half_height,  half_depth)
    glVertex3f(-half_width,  half_height,  half_depth)
    glVertex3f(-half_width,  half_height, -half_depth)
    glEnd()

def draw_sphere(radius):
  quad = gluNewQuadric()
  gluSphere(quad, radius, 20, 20)


def check_collision(x1, y1, z1, w1, h1, d1, x2, y2, z2, w2, h2, d2):
    """Checks for AABB collision between two 3D boxes."""
    if (x1 + w1 / 2 > x2 - w2 / 2 and
        x1 - w1 / 2 < x2 + w2 / 2 and
        y1 + h1 / 2 > y2 - h2 / 2 and
        y1 - h1 / 2 < y2 + h2 / 2 and
        z1 + d1 / 2 > z2 - d2 / 2 and
        z1 - d1 / 2 < z2 + d2 / 2):
        return True
    return False

# --- Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and grounded:
                player_y_speed = jump_force
                is_jumping = True
                grounded = False  # Immediately set to False
                jump_sound.play()
                wahoo_sound.play()


    # --- Player Movement ---
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] :
        player_x -= player_speed
    if keys[pygame.K_RIGHT] :
        player_x += player_speed
    if keys[pygame.K_UP]:
        player_z -= player_speed
    if keys[pygame.K_DOWN]:
        player_z += player_speed


    # Apply gravity
    player_y_speed += gravity
    player_y += player_y_speed

    # --- Collision Detection ---
    grounded_this_frame = False  # Flag for ground collision in this frame

    # Player-ground collision
    if player_y - player_height / 2 <= ground_y :
        player_y = ground_y + player_height / 2
        player_y_speed = 0
        is_jumping = False
        grounded_this_frame = True

    # Player-platform collision
    for platform in platforms:
        px, py, pz, pw, ph, pd = platform
        if check_collision(player_x, player_y, player_z, player_width, player_height, player_depth,
                           px, py, pz, pw, ph, pd):
            # Resolve collision (basic - can be improved)
            # Determine the direction of collision and resolve.  This is crucial
            # for correct platforming behavior.
            dx = (player_x - px) / (player_width / 2 + pw / 2)
            dy = (player_y - py) / (player_height / 2 + ph / 2)
            dz = (player_z - pz) / (player_depth / 2 + pd / 2)

            abs_dx = abs(dx)
            abs_dy = abs(dy)
            abs_dz = abs(dz)


            if abs_dy >= abs_dx and abs_dy >= abs_dz:
                if dy > 0:
                    player_y = py + ph / 2 + player_height / 2
                    player_y_speed = 0
                    is_jumping = False
                    grounded_this_frame = True

                elif dy < 0:
                    player_y = py - ph / 2 - player_height / 2
                    player_y_speed = 0


            elif abs_dx >= abs_dy and abs_dx >= abs_dz:
                if dx > 0:
                    player_x = px + pw / 2 + player_width / 2
                else:
                    player_x = px - pw/2 - player_width/2

            elif abs_dz >= abs_dy and abs_dz >= abs_dx:
                if dz > 0:
                    player_z = pz + pd/2 + player_depth / 2
                else:
                    player_z = pz - pd / 2 - player_depth /2

    grounded = grounded_this_frame


     # Player-coin collision
    for i, coin in enumerate(coins[:]):  # Iterate over a copy
        cx, cy, cz = coin
        if check_collision(player_x, player_y, player_z, player_width, player_height, player_depth,
                           cx, cy, cz, 0.6, 0.6, 0.6): #coin size
            collected_coins += 1
            coin_sound.play()
            coins.pop(i)  # Remove the collected coin


    # --- Camera Update (Simple follow camera) ---
    camera_x = player_x
    camera_z = player_z + 8 # Keep camera behind the player
    camera_target_x = player_x
    camera_target_y = player_y
    camera_target_z = player_z

    # --- Rendering ---

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    set_camera()
    draw_ground()
    draw_player()
    draw_platforms()
    draw_coins()

    # --- 2D Overlay (Score) ---
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, screen_width, screen_height, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)  # Disable depth testing for 2D
    draw_text(f"Coins: {collected_coins}", font, white, screen, 10, 10)
    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()
