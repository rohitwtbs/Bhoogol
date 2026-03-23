"""
Async entry point for Pygbag (WASM) builds.
Pygbag requires the main loop to be an async function with
`await asyncio.sleep(0)` yielding control to the browser each frame.

Usage (local test):  python -m pygbag --ume_block 0 .
The build output goes to build/web/
"""
import asyncio
import sys

# Apply WASM-specific settings *before* anything else imports settings
import wasm_settings  # noqa: F401

from settings import *
import moderngl as mgl
import pygame as pg
from shader_program import ShaderProgram
from scene import Scene
from player import Player
from textures import Textures


class VoxelEngine:
    def __init__(self, terrain_type=TERRAIN_GRASSLAND):
        self.terrain_type = terrain_type
        if terrain_type == TERRAIN_DESERT:
            self.bg_color = BG_COLOR_DESERT
        elif terrain_type == TERRAIN_FOREST:
            self.bg_color = BG_COLOR_FOREST
        elif terrain_type == TERRAIN_CYBERPUNK:
            self.bg_color = BG_COLOR_CYBERPUNK
        else:
            self.bg_color = BG_COLOR

        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, MAJOR_VER)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, MINOR_VER)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.gl_set_attribute(pg.GL_DEPTH_SIZE, DEPTH_SIZE)
        pg.display.gl_set_attribute(pg.GL_MULTISAMPLESAMPLES, NUM_SAMPLES)

        pg.display.set_mode(WIN_RES, flags=pg.OPENGL | pg.DOUBLEBUF)
        self.ctx = mgl.create_context()

        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE | mgl.BLEND)
        self.ctx.gc_mode = 'auto'

        self.clock = pg.time.Clock()
        self.delta_time = 0
        self.time = 0

        self.mouse_captured = True
        self.capture_mouse()

        self.is_running = True
        self.on_init()

    def capture_mouse(self):
        pg.event.set_grab(True)
        pg.mouse.set_visible(False)
        pg.mouse.get_rel()
        self.mouse_captured = True

    def release_mouse(self):
        pg.event.set_grab(False)
        pg.mouse.set_visible(True)
        pg.mouse.get_rel()
        self.mouse_captured = False

    def on_init(self):
        self.textures = Textures(self)
        self.player = Player(self)
        self.shader_program = ShaderProgram(self)
        self.scene = Scene(self)

    def update(self):
        self.player.update()
        self.shader_program.update()
        self.scene.update()

        self.delta_time = self.clock.tick()
        self.time = pg.time.get_ticks() * 0.001
        fps_text = f'{self.clock.get_fps() :.0f}'
        pg.display.set_caption(fps_text)

    def render(self):
        self.ctx.clear(color=self.bg_color)
        self.scene.render()
        pg.display.flip()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.is_running = False
                continue

            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                if self.mouse_captured:
                    self.release_mouse()
                continue

            if not self.mouse_captured and event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                self.capture_mouse()
                continue

            if not self.mouse_captured:
                continue

            self.player.handle_event(event=event)

    async def run(self):
        while self.is_running:
            self.handle_events()
            self.update()
            self.render()
            await asyncio.sleep(0)  # yield to browser event loop
        pg.quit()


async def main():
    # Skip terrain menu in WASM — default to grassland for now.
    # A web-based terrain selector can be added later.
    app = VoxelEngine(TERRAIN_GRASSLAND)
    await app.run()


asyncio.run(main())
