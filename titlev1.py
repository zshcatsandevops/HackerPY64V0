from ursina import *
from ursina.shaders import lit_with_shadows_shader
import numpy as np
from dataclasses import dataclass
from typing import Dict, Optional, List

@dataclass
class FaceConfig:
    HEAD_SCALE: float = 1.0
    FEATURE_SCALE: float = 0.2
    NOSE_HEIGHT: float = 0.3
    NOSE_RADIUS: float = 0.1
    MOUTH_SCALE: tuple = (0.3, 0.1, 0.05)
    DRAG_PLANE_SCALE: float = 50.0
    MOUTH_ANIM_SPEED: float = 1.0
    MOUTH_ANIM_AMPLITUDE: float = 0.05

class FaceController:
    def __init__(self, config: FaceConfig):
        self.config = config
        self.setup_face()
        self.setup_lighting()
        self.setup_drag_system()
        
    def setup_face(self):
        # Create head with optimized shader
        self.head = Entity(
            model='sphere',
            color=color.rgb(255, 224, 189),
            scale=self.config.HEAD_SCALE,
            shader=lit_with_shadows_shader,
            position=(0, 0, 0)
        )
        
        # Create facial features with shared properties
        feature_props = {
            'shader': lit_with_shadows_shader,
            'parent': self.head
        }
        
        # Create features using list comprehension for efficiency
        self.features = {
            'left_eye': Entity(
                model='sphere',
                color=color.white,
                scale=self.config.FEATURE_SCALE,
                position=(-0.2, 0.2, 0.45),
                collider='sphere',
                **feature_props
            ),
            'right_eye': Entity(
                model='sphere',
                color=color.white,
                scale=self.config.FEATURE_SCALE,
                position=(0.2, 0.2, 0.45),
                collider='sphere',
                **feature_props
            ),
            'nose': Entity(
                model=Cone(
                    resolution=8,
                    radius=self.config.NOSE_RADIUS,
                    height=self.config.NOSE_HEIGHT
                ),
                color=color.rgb(255, 200, 200),
                position=(0, 0.0, 0.5),
                rotation=(90, 0, 0),
                collider='mesh',
                **feature_props
            ),
            'mouth': Entity(
                model='cube',
                color=color.red,
                scale=self.config.MOUTH_SCALE,
                position=(0, -0.2, 0.45),
                collider='box',
                **feature_props
            )
        }
        
        # Store initial positions for animation
        self.initial_positions = {
            name: Vec3(*feature.position) for name, feature in self.features.items()
        }
        
    def setup_lighting(self):
        # Optimized lighting setup
        self.sunlight = DirectionalLight(shadows=True)
        self.sunlight.look_at(Vec3(1, -1, 1))
        self.ambient = AmbientLight(color=color.dark_gray)
        
    def setup_drag_system(self):
        self.dragging_feature = None
        self.drag_plane = None
        self.animation_time = 0
        
    def handle_input(self, key):
        if key == 'left mouse down':
            if mouse.hovered_entity in self.features.values():
                self.start_drag(mouse.hovered_entity)
        elif key == 'left mouse up':
            self.end_drag()
            
    def start_drag(self, entity):
        self.dragging_feature = entity
        self.dragging_feature.collision = False
        self.drag_plane = Entity(
            model='quad',
            collider='mesh',
            position=entity.world_position,
            rotation=camera.world_rotation,
            scale=self.config.DRAG_PLANE_SCALE,
            visible=False
        )
        
    def end_drag(self):
        if self.dragging_feature:
            self.dragging_feature.collision = True
            self.dragging_feature = None
            destroy(self.drag_plane)
            self.drag_plane = None
            
    def update(self, dt):
        if self.dragging_feature and mouse.world_point is not None:
            self.dragging_feature.world_position = mouse.world_point
            
        # Optimized mouth animation using numpy
        if self.dragging_feature is not self.features['mouth']:
            mouth = self.features['mouth']
            base_pos = self.initial_positions['mouth']
            self.animation_time += dt
            mouth.y = base_pos.y + self.config.MOUTH_ANIM_AMPLITUDE * \
                     np.sin(self.animation_time * 2 * np.pi * self.config.MOUTH_ANIM_SPEED)

def main():
    app = Ursina()
    window.title = "Ursina 3D Face Manipulator (M1 Optimized)"
    window.color = color.black
    
    editor_camera = EditorCamera()
    config = FaceConfig()
    controller = FaceController(config)
    
    def update():
        controller.update(time.dt)
    
    def input_handler(key):
        controller.handle_input(key)
    
    # Set up event handlers
    app.update = update
    app.input = input_handler
    
    app.run()

if __name__ == "__main__":
    main()
