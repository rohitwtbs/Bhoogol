"""
Minecraft World Viewer for Bhoogol
Loads and displays Minecraft worlds using the Bhoogol voxel engine.

Usage:
    python minecraft_viewer.py /path/to/minecraft/world
    
Controls:
    WASD - Move forward/left/back/right
    QE - Move down/up
    Mouse - Look around
    E - Place block
    R - Remove block
    ESC - Exit
"""

import sys
import os
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from settings import *
import moderngl as mgl
import pygame as pg
from shader_program import ShaderProgram
from player import Player
from textures import Textures
from minecraft_world import MinecraftWorldWrapper


class MinecraftViewer:
    """Main Minecraft world viewer application."""
    
    def __init__(self, minecraft_world_path):
        """Initialize the viewer."""
        self.minecraft_world_path = minecraft_world_path
        self.terrain_type = TERRAIN_GRASSLAND  # Not used for Minecraft but required
        self.bg_color = glm.vec3(0.1, 0.16, 0.8)
        
        # Validate path
        if not os.path.isdir(minecraft_world_path):
            raise FileNotFoundError(f"World path not found: {minecraft_world_path}")
        
        if not os.path.exists(os.path.join(minecraft_world_path, 'level.dat')):
            raise FileNotFoundError(
                f"No level.dat found. Make sure {minecraft_world_path} is a valid Minecraft world."
            )
        
        # Initialize Pygame and OpenGL
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, MAJOR_VER)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, MINOR_VER)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.gl_set_attribute(pg.GL_DEPTH_SIZE, DEPTH_SIZE)
        
        self.screen = pg.display.set_mode(WIN_RES, flags=pg.OPENGL | pg.DOUBLEBUF)
        pg.display.set_caption('Minecraft World Viewer - Bhoogol')
        self.ctx = mgl.create_context()
        self.ctx.enable(mgl.DEPTH_TEST | mgl.CULL_FACE | mgl.BLEND)
        self.ctx.gc_mode = 'auto'
        self.clock = pg.time.Clock()
        
        # Initialize player first (needed by shader program)
        self.player = Player(self)
        
        # Load shaders and textures
        self.shader_program = ShaderProgram(self)
        self.textures = Textures(self)
        
        # Load world
        print(f"Loading Minecraft world from: {minecraft_world_path}")
        self.world = MinecraftWorldWrapper(self, minecraft_world_path)
        
        # Create a simple scene wrapper for compatibility with Player
        class SceneWrapper:
            def __init__(self, world):
                self.world = world
        
        self.scene = SceneWrapper(self.world)
        
        # Set player spawn position
        spawn_x, spawn_y, spawn_z = self.world.spawn_pos
        # Ensure player is above ground by using a safe Y position
        safe_y = max(spawn_y + 64, 100)
        self.player.position = glm.vec3(spawn_x, safe_y, spawn_z)
        print(f"Player spawned at: {spawn_x}, {safe_y}, {spawn_z}")
        
        self.running = True
        self.mouse_captured = True
        self.capture_mouse()
    
    def capture_mouse(self):
        """Capture mouse for camera control."""
        pg.event.set_grab(True)
        pg.mouse.set_visible(False)
        pg.mouse.get_rel()
        self.mouse_captured = True
    
    def release_mouse(self):
        """Release mouse capture."""
        pg.event.set_grab(False)
        pg.mouse.set_visible(True)
        pg.mouse.get_rel()
        self.mouse_captured = False
    
    def handle_events(self):
        """Handle input events."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.running = False
            # Let player handle mouse events
            self.player.handle_event(event)
    
    def update(self):
        """Update world state."""
        self.delta_time = self.clock.tick(60) / 1000.0
        self.player.update()
        self.world.update()
    
    def render(self):
        """Render the world."""
        self.ctx.clear(color=tuple(self.bg_color))
        self.world.render()
        pg.display.flip()
    
    def run(self):
        """Main application loop."""
        print("Starting Minecraft World Viewer...")
        print("Controls: WASD + Space/Q for up/down, Mouse for look")
        print("Press ESC to exit")
        
        frame = 0
        while self.running:
            try:
                self.handle_events()
                self.update()
                self.render()
                frame += 1
            except Exception as e:
                import traceback
                print(f"Error on frame {frame}: {e}")
                traceback.print_exc()
                break
        
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        print("Shutting down...")
        self.ctx.release()
        pg.quit()


def main():
    """Entry point for the viewer."""
    parser = argparse.ArgumentParser(
        description='Minecraft World Viewer - View Minecraft worlds in Bhoogol',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python minecraft_viewer.py ~/.minecraft/saves/My_World
  python minecraft_viewer.py /path/to/world
        ''')
    
    parser.add_argument(
        'world_path',
        help='Path to Minecraft world directory containing level.dat'
    )
    
    args = parser.parse_args()
    
    try:
        viewer = MinecraftViewer(args.world_path)
        viewer.run()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
