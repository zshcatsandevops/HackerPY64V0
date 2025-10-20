#!/usr/bin/env python3
# -------------------------------------------------------------
# Super Mario 64 Tech Stage 1-1 (Ursina Prototype)
# -------------------------------------------------------------
# (C) 2025 FlamesCo / Samsoft — GPL-3.0-or-later
# Simulates SM64-like movement, camera, physics, collectibles, and enemies.
# Inspired by early tech stages used internally by Nintendo (1995-96).
# -------------------------------------------------------------
from ursina import *
from random import uniform

app = Ursina()

# -------------------------------------------------------------
# WINDOW SETTINGS
# -------------------------------------------------------------
window.title = "Super Mario 64 – Tech Stage 1-1 (Ursina)"
window.size = (600, 400)
window.borderless = False
window.fullscreen = False
window.color = color.rgb(135, 206, 235)

# -------------------------------------------------------------
# ENVIRONMENT
# -------------------------------------------------------------
sky = Sky()
ambient_light = AmbientLight(color=color.rgba(180, 180, 180, 255))
directional_light = DirectionalLight(direction=Vec3(-1, -1, -1), color=color.white)

ground = Entity(
    model='plane',
    texture='white_cube',
    texture_scale=(40, 40),
    scale=(80, 1, 80),
    color=color.rgb(100, 200, 100),
    position=(0, -1, 0),
    collider='box'
)

# -------------------------------------------------------------
# MARIO-LIKE CONTROLLER
# -------------------------------------------------------------
class Mario(Entity):
    def __init__(self):
        super().__init__(
            model='cube',
            color=color.red,
            scale_y=1.8,
            position=(0, 3, 0),
            collider='box'
        )
        self.speed = 6
        self.jump_height = 10
        self.gravity = 25
        self.vertical_velocity = 0
        self.is_jumping = False
        self.triple_jump_count = 0

    def update(self):
        move = Vec3(
            held_keys['d'] - held_keys['a'],
            0,
            held_keys['s'] - held_keys['w']
        ).normalized()

        # Move relative to camera rotation
        move = move.x * camera.right + move.z * camera.forward
        self.position += move * time.dt * self.speed

        # Apply gravity
        self.vertical_velocity -= self.gravity * time.dt
        self.y += self.vertical_velocity * time.dt

        # Ground check
        hit_info = raycast(self.world_position + (0, 0.5, 0), Vec3(0, -1, 0), distance=1, ignore=(self,))
        if hit_info.hit:
            if self.vertical_velocity < 0:
                self.y = hit_info.world_point.y + 0.01
                self.vertical_velocity = 0
                self.is_jumping = False
                self.triple_jump_count = 0

        # Jump (single / double / triple)
        if held_keys['space'] and not self.is_jumping:
            self.vertical_velocity = self.jump_height
            self.is_jumping = True
            self.triple_jump_count += 1
            invoke(self.reset_jump, delay=0.3)

    def reset_jump(self):
        self.is_jumping = False

player = Mario()

# -------------------------------------------------------------
# THIRD-PERSON CAMERA (Mario 64-style)
# -------------------------------------------------------------
camera.parent = player
camera.position = (0, 3, -8)
camera.rotation = (10, 0, 0)
camera_pivot = Entity(parent=player, y=2)

def camera_follow():
    camera.look_at(camera_pivot)
    camera.rotation_y += (held_keys['q'] - held_keys['e']) * 60 * time.dt

camera.update = camera_follow

# -------------------------------------------------------------
# COLLECTIBLES
# -------------------------------------------------------------
coins = []
for i in range(10):
    coin = Entity(
        model='sphere',
        color=color.yellow,
        scale=0.5,
        position=(uniform(-10, 10), 1, uniform(-10, 10)),
        collider='sphere'
    )
    coins.append(coin)

coin_count = 0
coin_text = Text(text=f"Coins: {coin_count}", position=(-.85, .45), scale=1.2)

def check_coins():
    global coin_count
    for coin in coins:
        if coin.enabled and distance(player.position, coin.position) < 1:
            coin.disable()
            coin_count += 1
            coin_text.text = f"Coins: {coin_count}"

# -------------------------------------------------------------
# GOOMBA ENEMY
# -------------------------------------------------------------
goombas = []
for i in range(5):
    g = Entity(
        model='cube',
        color=color.brown,
        scale=(1, 0.5, 1),
        position=(uniform(-15, 15), 0.25, uniform(-15, 15)),
        collider='box'
    )
    g.speed = 2
    g.direction = Vec3(uniform(-1, 1), 0, uniform(-1, 1)).normalized()
    goombas.append(g)

def update_goombas():
    for g in goombas:
        g.position += g.direction * time.dt * g.speed
        # Bounce off bounds
        if abs(g.x) > 20 or abs(g.z) > 20:
            g.direction *= -1
        # Player stomp
        if distance(player.position, g.position) < 1 and player.y > g.y + 0.5:
            g.disable()
            player.vertical_velocity = player.jump_height * 0.5  # bounce
        elif distance(player.position, g.position) < 0.7 and player.y <= g.y + 0.5:
            print("Ouch! Hit by Goomba")
            player.position = Vec3(0, 3, 0)

# -------------------------------------------------------------
# SIMPLE PLATFORMS
# -------------------------------------------------------------
platforms = []
for i in range(3):
    p = Entity(
        model='cube',
        color=color.azure,
        scale=(3, 0.3, 3),
        position=(i * 6 - 6, uniform(1, 4), uniform(-5, 5)),
        collider='box'
    )
    platforms.append(p)

# -------------------------------------------------------------
# UPDATE LOOP
# -------------------------------------------------------------
def update():
    check_coins()
    update_goombas()

# -------------------------------------------------------------
# UI & TEST STAGE SIGN
# -------------------------------------------------------------
Text("SM64 Tech Stage 1-1", origin=(0, 0), position=(0, .45), scale=1.5)
Text("WASD Move | SPACE Jump | Q/E Rotate Cam", origin=(0, 0), position=(0, .4), scale=0.8)

# -------------------------------------------------------------
app.run()
