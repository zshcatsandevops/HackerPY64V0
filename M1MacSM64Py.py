from ursina import *  # Import Ursina engine classes and functions

# Constants for easy tuning
MOVE_SPEED = 5      # horizontal movement speed
JUMP_SPEED = 8      # jump impulse strength
GRAVITY    = 15     # gravity strength (units per second^2)

class Player(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            model='cube',
            color=color.orange,
            scale=(1,1,1),
            origin_y=-0.5,    # origin at base of the cube (feet level)
            collider='box',   # add a box collider fitting the model
            **kwargs)
        # Movement attributes
        self.move_speed = MOVE_SPEED
        self.jump_speed = JUMP_SPEED
        self.gravity = GRAVITY
        self.velocity_y = 0    # vertical velocity
        self.grounded = False  # whether player is on the ground

    def update(self):
        # --- Horizontal Movement ---
        direction = Vec3(
            self.forward * (held_keys['w'] - held_keys['s']) + 
            self.right   * (held_keys['d'] - held_keys['a'])
        ).normalized()  # calculate direction vector from WASD input

        if direction.length() > 0:
            # Check for wall/obstacle in the direction of movement
            hit_info = raycast(self.position + self.up * 0.5, direction, 
                               ignore=(self,), distance=0.5)
            if not hit_info.hit:
                # Move the player if no obstacle hit
                self.position += direction * self.move_speed * time.dt

        # --- Vertical Movement (Jumping/Gravity) ---
        # If on ground, allow jumping
        if self.grounded and held_keys['space']:
            self.velocity_y = self.jump_speed
            self.grounded = False

        # Apply gravity always
        self.velocity_y -= self.gravity * time.dt
        # Move vertically
        self.y += self.velocity_y * time.dt

        # Collision check below (raycast downwards)
        # Start a bit above the player's base to avoid self-collision
        ray_origin = self.position + (0, 0.1, 0)
        ground_hit = raycast(ray_origin, Vec3(0, -1, 0), ignore=(self,))
        if ground_hit.hit:
            # If falling and hit ground (or platform)
            if self.velocity_y < 0:
                # Land on the ground/platform
                self.grounded = True
                self.velocity_y = 0
                # Align player's feet with the top of the ground/platform
                self.y = ground_hit.entity.world_y + ground_hit.entity.scale_y * 0.5

        else:
            # No ground directly below -> in air
            self.grounded = False

        # --- Basic "Animation" ---
        # Tilt forward when moving, upright when stopped
        if direction.length() > 0 and self.grounded:
            self.rotation_x = min(10, self.rotation_x + 1)  # tilt a bit (up to 10 degrees)
        else:
            self.rotation_x = max(0, self.rotation_x - 2)   # ease back to 0 when not moving
        # When jumping/falling, tilt based on vertical velocity
        if not self.grounded:
            self.rotation_x = clamp(self.velocity_y * 5, -30, 30)  # tilt forward/backward in air

# Initialize the Ursina app
app = Ursina()

# Set up the environment
# Ground (large platform)
ground = Entity(model='cube', color=color.green, texture='white_cube', 
                scale=(20, 1, 20), position=(0,0,0), origin_y=-0.5, collider='box')
# Some floating platforms
platform1 = Entity(model='cube', color=color.gray, texture='white_cube',
                   scale=(3, 1, 3), position=(4, 2, 0), origin_y=-0.5, collider='box')
platform2 = Entity(model='cube', color=color.gray, texture='white_cube',
                   scale=(3, 1, 3), position=(8, 4, 0), origin_y=-0.5, collider='box')
# An obstacle (wall or pillar)
obstacle = Entity(model='cube', color=color.red, texture='white_cube',
                  scale=(1, 3, 1), position=(0, 1.5, 5), origin_y=-0.5, collider='box')

# Create the player
player = Player(position=(0, 1, 0))  # start slightly above ground at center

# Camera setup: third-person view
camera.parent = player    # make the camera follow the player
camera.position = (0, 3, -10)  # offset the camera: 3 units up, 10 units behind the player
camera.rotation_x = 20    # tilt the camera down a bit for a better view

# (Optional) add some light and sky for ambience
DirectionalLight().look_at(Vec3(1,-1,-1))
Sky(color=color.cyan)  # blue sky background

# Run the game
app.run()
