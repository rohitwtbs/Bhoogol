from settings import *
import moderngl as mgl
from world import World
from world_objects.voxel_marker import VoxelMarker
from world_objects.water import Water
from world_objects.clouds import Clouds
from world_objects.voxel_player import VoxelPlayer
from terrain_gen import get_height
import pygame as pg


class Scene:
    def __init__(self, app):
        self.app = app
        self.world = World(self.app)
        self.voxel_marker = VoxelMarker(self.world.voxel_handler)
        self.water = Water(app)
        self.clouds = Clouds(app)

        # --- spawn two voxel fighters in the Desert scene only ---
        self.fighter_blue = None
        self.fighter_red  = None
        self.voxel_players = []

        if app.terrain_type == TERRAIN_DESERT:
            p1x = float(CENTER_XZ - 18)
            p2x = float(CENTER_XZ + 18)
            pz  = float(CENTER_XZ)
            p1y = float(get_height(int(p1x), int(pz), app.terrain_type))
            p2y = float(get_height(int(p2x), int(pz), app.terrain_type))

            self.fighter_blue = VoxelPlayer(app, (p1x, p1y, pz), scheme='blue', name='Blue')
            self.fighter_red  = VoxelPlayer(app, (p2x, p2y, pz), scheme='red',  name='Red')
            self.fighter_blue.set_enemy(self.fighter_red)
            self.fighter_red.set_enemy(self.fighter_blue)
            self.voxel_players = [self.fighter_blue, self.fighter_red]

    def update(self):
        self.world.update()
        self.voxel_marker.update()
        self.clouds.update()

        dt = self.app.delta_time * 0.001   # ms → seconds
        for fighter in self.voxel_players:
            fighter.update(dt)

        # update window title with combat status (desert only)
        if self.fighter_blue and self.fighter_red:
            b = self.fighter_blue
            r = self.fighter_red
            b_state = 'DEAD' if b.dead else b.state.upper()
            r_state = 'DEAD' if r.dead else r.state.upper()
            pg.display.set_caption(
                f'FPS:{self.app.clock.get_fps():.0f}  |  '
                f'[Blue] HP:{b.hp}/{b.max_hp}  K:{b.kill_count}  {b_state}  |  '
                f'[Red]  HP:{r.hp}/{r.max_hp}  K:{r.kill_count}  {r_state}'
            )
        else:
            pg.display.set_caption(f'{self.app.clock.get_fps():.0f}')

    def render(self):
        # chunks rendering
        self.world.render()

        # rendering without cull face (clouds, water, player bodies)
        self.app.ctx.disable(mgl.CULL_FACE)
        self.clouds.render()
        self.water.render()

        # voxel fighter characters
        for fighter in self.voxel_players:
            fighter.render()

        self.app.ctx.enable(mgl.CULL_FACE)

        # voxel selection marker
        self.voxel_marker.render()
