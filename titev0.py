import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from dataclasses import dataclass
import numpy as np
import math

@dataclass
class Vec3:
    x: float
    y: float
    z: float
    
    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

class FaceController:
    def __init__(self):
        self.vertices = np.array([
            # Face vertices (simplified for example)
            [-1.0, -1.0, 0.0],
            [1.0, -1.0, 0.0],
            [1.0, 1.0, 0.0],
            [-1.0, 1.0, 0.0],
        ], dtype=np.float32)
        
        self.control_points = {
            'nose': Vec3(0.0, 0.0, 0.0),
            'left_ear': Vec3(-1.0, 0.0, 0.0),
            'right_ear': Vec3(1.0, 0.0, 0.0)
        }
        
        self.original_positions = self.control_points.copy()
        self.selected_point = None
        
    def draw(self):
        glBegin(GL_QUADS)
        glColor3f(1.0, 0.0, 0.0)
        for v in self.vertices:
            glVertex3f(v[0], v[1], v[2])
        glEnd()
        
        # Draw control points
        glPointSize(10.0)
        glBegin(GL_POINTS)
        for point in self.control_points.values():
            glVertex3f(point.x, point.y, point.z)
        glEnd()
    
    def handle_mouse(self, x, y, button_down):
        if button_down:
            # Convert screen coordinates to world space
            modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
            projection = glGetDoublev(GL_PROJECTION_MATRIX)
            viewport = glGetIntegerv(GL_VIEWPORT)
            
            world_pos = gluUnProject(x, viewport[3] - y, 0.0,
                                   modelview, projection, viewport)
            
            mouse_pos = Vec3(world_pos[0], world_pos[1], 0.0)
            
            # Find closest control point
            if not self.selected_point:
                min_dist = float('inf')
                for name, point in self.control_points.items():
                    dist = (Vec3(point.x, point.y, point.z) - mouse_pos).length()
                    if dist < min_dist and dist < 0.2:  # Threshold for selection
                        min_dist = dist
                        self.selected_point = name
            
            # Update selected point position
            if self.selected_point:
                point = self.control_points[self.selected_point]
                orig = self.original_positions[self.selected_point]
                
                # Limit movement range
                new_pos = mouse_pos
                dist = (new_pos - Vec3(orig.x, orig.y, orig.z)).length()
                if dist > 1.0:
                    dir = (new_pos - Vec3(orig.x, orig.y, orig.z))
                    dir = dir * (1.0 / dir.length())
                    new_pos = Vec3(orig.x, orig.y, orig.z) + dir
                
                self.control_points[self.selected_point] = new_pos
        else:
            self.selected_point = None

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    
    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)
    
    face = FaceController()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        # Handle mouse input
        mouse_pos = pygame.mouse.get_pos()
        button_down = pygame.mouse.get_pressed()[0]
        face.handle_mouse(mouse_pos[0], mouse_pos[1], button_down)
        
        # Clear screen and draw
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        face.draw()
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()
