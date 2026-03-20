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
    W, H = 660, 420
    screen = pg.display.set_mode((W, H))
    pg.display.set_caption('Bhoogol — Choose Terrain')
    pg.mouse.set_visible(True)
    pg.event.set_grab(False)

    font_title = pg.font.SysFont('Arial', 48, bold=True)
    font_sub   = pg.font.SysFont('Arial', 20)
    font_btn   = pg.font.SysFont('Arial', 28, bold=True)
    font_desc  = pg.font.SysFont('Arial', 17)

    grass_btn  = pg.Rect(60,  195, 240, 70)
    desert_btn = pg.Rect(360, 195, 240, 70)

    grass_desc  = ['Rolling hills & forests,', 'snow peaks, caves & rivers']
    desert_desc = ['Vast sandy dunes,', 'deep stone depths']

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
                if grass_btn.collidepoint(mx, my):
                    choice = TERRAIN_GRASSLAND
                elif desert_btn.collidepoint(mx, my):
                    choice = TERRAIN_DESERT

        screen.fill((18, 20, 32))

        # subtle divider
        pg.draw.line(screen, (45, 50, 75), (W // 2, 155), (W // 2, 370), 1)

        # title
        title = font_title.render('Bhoogol', True, (210, 215, 255))
        screen.blit(title, title.get_rect(center=(W // 2, 62)))
        sub = font_sub.render('Select a terrain type to explore', True, (140, 150, 185))
        screen.blit(sub, sub.get_rect(center=(W // 2, 115)))

        # buttons
        g_hover = grass_btn.collidepoint(mx, my)
        d_hover = desert_btn.collidepoint(mx, my)
        pg.draw.rect(screen, (50, 135, 55) if g_hover else (38, 100, 42),  grass_btn,  border_radius=12)
        pg.draw.rect(screen, (195, 160, 65) if d_hover else (155, 120, 45), desert_btn, border_radius=12)
        pg.draw.rect(screen, (110, 215, 110), grass_btn,  2, border_radius=12)
        pg.draw.rect(screen, (235, 195, 90),  desert_btn, 2, border_radius=12)

        gl = font_btn.render('Grassland', True, (240, 255, 240))
        dl = font_btn.render('Desert',    True, (255, 248, 220))
        screen.blit(gl, gl.get_rect(center=grass_btn.center))
        screen.blit(dl, dl.get_rect(center=desert_btn.center))

        # descriptions
        for btn, lines, col in [
            (grass_btn,  grass_desc,  (175, 215, 175)),
            (desert_btn, desert_desc, (215, 200, 155)),
        ]:
            for j, line in enumerate(lines):
                t = font_desc.render(line, True, col)
                screen.blit(t, t.get_rect(center=(btn.centerx, btn.bottom + 24 + j * 22)))

        pg.display.flip()
        clock.tick(60)

    pg.quit()
    return choice

class VoxelEngine:
    def __init__(self, terrain_type=TERRAIN_GRASSLAND):
        self.terrain_type = terrain_type
        self.bg_color = BG_COLOR if terrain_type == TERRAIN_GRASSLAND else BG_COLOR_DESERT

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

        pg.event.set_grab(True)
        pg.mouse.set_visible(False)

        self.is_running = True
        self.on_init()

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
        pg.display.set_caption(f'{self.clock.get_fps() :.0f}')

    def render(self):
        self.ctx.clear(color=self.bg_color)
        self.scene.render()
        pg.display.flip()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.is_running = False
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
