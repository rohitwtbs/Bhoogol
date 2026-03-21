from settings import *
import moderngl as mgl
import pygame as pg
import sys
from shader_program import ShaderProgram
from scene import Scene
from player import Player
from textures import Textures


def show_terrain_menu():
    pg.init()
    W, H = 1100, 460
    screen = pg.display.set_mode((W, H))
    pg.display.set_caption('Bhoogol — Choose Terrain')
    pg.mouse.set_visible(True)
    pg.event.set_grab(False)

    font_title = pg.font.SysFont('Arial', 48, bold=True)
    font_sub   = pg.font.SysFont('Arial', 20)
    font_btn   = pg.font.SysFont('Arial', 24, bold=True)
    font_desc  = pg.font.SysFont('Arial', 15)

    # 4 buttons, evenly spaced
    BW, BH = 210, 70
    GAP    = 18
    START  = (W - 4 * BW - 3 * GAP) // 2
    grass_btn  = pg.Rect(START,                 210, BW, BH)
    forest_btn = pg.Rect(START +  (BW + GAP),   210, BW, BH)
    desert_btn = pg.Rect(START + 2*(BW + GAP),  210, BW, BH)
    cyber_btn  = pg.Rect(START + 3*(BW + GAP),  210, BW, BH)

    options = [
        (grass_btn,  TERRAIN_GRASSLAND, 'Grassland',
         (50, 135, 55),   (38, 100, 42),  (110, 215, 110),
         (240, 255, 240), (175, 215, 175),
         ['Rolling hills & forests,', 'snow peaks & caves']),
        (forest_btn, TERRAIN_FOREST,    'Dense Forest',
         (30, 100, 40),   (20,  70, 28),  (80,  200, 100),
         (210, 255, 210), (140, 210, 150),
         ['Thick canopy & dense trees,', 'hilly misty terrain']),
        (desert_btn, TERRAIN_DESERT,    'Desert',
         (195, 160, 65),  (155, 120, 45), (235, 195, 90),
         (255, 248, 220), (215, 200, 155),
         ['Vast sandy dunes,', 'deep stone depths']),
        (cyber_btn,  TERRAIN_CYBERPUNK, 'Cyberpunk',
         (60,  10, 120),  (35,   5,  80), (180,  40, 255),
         (220, 180, 255), (160, 100, 220),
         ['Neon city grid, drones,', 'RGB hyperloops!']),
    ]

    clock = pg.time.Clock()
    choice = None
    while choice is None:
        mx, my = pg.mouse.get_pos()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                for btn, terrain_id, *_ in options:
                    if btn.collidepoint(mx, my):
                        choice = terrain_id

        screen.fill((10, 8, 22))

        title = font_title.render('Bhoogol', True, (210, 215, 255))
        screen.blit(title, title.get_rect(center=(W // 2, 65)))
        sub = font_sub.render('Select a terrain type to explore', True, (140, 150, 185))
        screen.blit(sub, sub.get_rect(center=(W // 2, 130)))

        for btn, _, label, col_hover, col_norm, col_border, col_text, col_desc, desc_lines in options:
            hover = btn.collidepoint(mx, my)
            pg.draw.rect(screen, col_hover if hover else col_norm, btn, border_radius=12)
            pg.draw.rect(screen, col_border, btn, 2, border_radius=12)
            lbl = font_btn.render(label, True, col_text)
            screen.blit(lbl, lbl.get_rect(center=btn.center))
            for j, line in enumerate(desc_lines):
                t = font_desc.render(line, True, col_desc)
                screen.blit(t, t.get_rect(center=(btn.centerx, btn.bottom + 22 + j * 18)))

        pg.display.flip()
        clock.tick(60)

    pg.quit()
    return choice

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
        if self.mouse_captured:
            pg.display.set_caption(fps_text)
        else:
            pg.display.set_caption(f'{fps_text} | Cursor Free - Left Click to Resume')

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

    def run(self):
        while self.is_running:
            self.handle_events()
            self.update()
            self.render()
        pg.quit()
        sys.exit()


if __name__ == '__main__':
    terrain_type = show_terrain_menu()
    app = VoxelEngine(terrain_type)
    app.run()
