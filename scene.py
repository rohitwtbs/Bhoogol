from settings import *
import moderngl as mgl
import pygame as pg
from world import World
from world_objects.voxel_marker import VoxelMarker
from world_objects.water import Water
from world_objects.clouds import Clouds
from world_objects.drone import Drone
from world_objects.hyperloop import Hyperloop
from world_objects.bike import Bike
from world_objects.hot_air_balloon import HotAirBalloon
from world_objects.city_dome import CityDome


class Scene:
    def __init__(self, app):
        self.app = app
        self.world = World(self.app)
        self.voxel_marker = VoxelMarker(self.world.voxel_handler)
        self.water  = Water(app)
        self.clouds = Clouds(app)

        # populated per terrain type below
        self.drones      = []
        self.hyperloops  = []
        self.bikes       = []
        self.balloons    = []
        self.dome        = None

        if app.terrain_type == TERRAIN_CYBERPUNK:
            self._spawn_cyberpunk()

    def _spawn_cyberpunk(self):
        """Drones + hyperloops + bikes + hot-air balloons over the neon city."""
        # ---- Flying drones ----
        configs = [
            (   0,   0, 30, 20, 0, 1.00),
            ( 32,  28, 38, 14, 1, 0.70),
            (-28,  20, 34, 18, 2, 1.20),
            ( 20, -32, 44, 22, 3, 0.90),
            (-22, -22, 50, 12, 4, 1.40),
            (  0,  42, 40, 26, 5, 0.60),
        ]
        for ox, oz, dh, rad, pal, spd in configs:
            pos = (CENTER_XZ + ox, CYBER_GROUND_LVL + dh, CENTER_XZ + oz)
            self.drones.append(Drone(self.app, pos,
                                     palette_idx=pal,
                                     patrol_radius=rad,
                                     speed=spd))

        # ---- Hyperloops ----
        span = 160
        hl_y = CYBER_GROUND_LVL + 40
        self.hyperloops.append(Hyperloop(
            self.app,
            position=(CENTER_XZ - span // 2, hl_y, CENTER_XZ),
            length=span, color_idx=0, axis='x'
        ))
        self.hyperloops.append(Hyperloop(
            self.app,
            position=(CENTER_XZ + 3, hl_y + 5, CENTER_XZ - span // 2),
            length=span, color_idx=1, axis='z'
        ))

        # ---- Street Bikes (on road level, 4 lanes) ----
        road_y = float(CYBER_GROUND_LVL + 1)
        # Two X-axis lanes (different Z offsets)
        bike_lanes_x = [
            (CENTER_XZ - 70, road_y, CENTER_XZ - 2,  0, 20.0),
            (CENTER_XZ - 70, road_y, CENTER_XZ + 4,  1, 26.0),
            (CENTER_XZ - 70, road_y, CENTER_XZ + 10, 2, 18.0),
        ]
        for sx, sy, sz, pal, spd in bike_lanes_x:
            self.bikes.append(Bike(self.app, (sx, sy, sz),
                                   palette_idx=pal, speed=spd,
                                   axis='x', lane_length=140))
        # Two Z-axis lanes
        bike_lanes_z = [
            (CENTER_XZ - 2,  road_y, CENTER_XZ - 70, 3, 22.0),
            (CENTER_XZ + 4,  road_y, CENTER_XZ - 70, 0, 28.0),
        ]
        for sx, sy, sz, pal, spd in bike_lanes_z:
            self.bikes.append(Bike(self.app, (sx, sy, sz),
                                   palette_idx=pal, speed=spd,
                                   axis='z', lane_length=140))

        # ---- Hot-Air Balloons (high altitude drift) ----
        balloon_configs = [
            (CENTER_XZ - 60, CYBER_GROUND_LVL + 80, CENTER_XZ - 20,  0, 1.2, 'x'),
            (CENTER_XZ + 20, CYBER_GROUND_LVL + 95, CENTER_XZ - 50,  1, 0.8, 'z'),
            (CENTER_XZ - 30, CYBER_GROUND_LVL + 75, CENTER_XZ + 30,  2, 1.5, 'x'),
            (CENTER_XZ + 50, CYBER_GROUND_LVL + 88, CENTER_XZ + 10,  3, 1.0, 'z'),
        ]
        for bx, by, bz, cidx, spd, ax in balloon_configs:
            self.balloons.append(HotAirBalloon(
                self.app, (bx, by, bz),
                color_idx=cidx, drift_speed=spd, axis=ax
            ))

        # ---- Changi-style glass torus dome (city landmark) ----
        # Placed one city-block north-east of centre so it anchors the skyline
        dome_pos = (
            float(CENTER_XZ + 55),
            float(CYBER_GROUND_LVL + 1),
            float(CENTER_XZ + 55)
        )
        self.dome = CityDome(self.app, dome_pos)

    # ------------------------------------------------------------------
    # Update / Render
    # ------------------------------------------------------------------

    def update(self):
        self.world.update()
        self.voxel_marker.update()
        if self.app.terrain_type != TERRAIN_CYBERPUNK:
            self.clouds.update()

        dt = self.app.delta_time * 0.001   # ms → s

        for drone in self.drones:
            drone.update(dt)
        for bike in self.bikes:
            bike.update(dt)
        for balloon in self.balloons:
            balloon.update(dt)

        self._update_caption()

    def _update_caption(self):
        tt = self.app.terrain_type
        fps = self.app.clock.get_fps()
        if tt == TERRAIN_CYBERPUNK:
            pg.display.set_caption(
                f'FPS:{fps:.0f}  |  CYBERPUNK CITY  |  '
                f'Drones:{len(self.drones)}  '
                f'Bikes:{len(self.bikes)}  '
                f'Balloons:{len(self.balloons)}'
            )
        elif tt == TERRAIN_DESERT:
            pg.display.set_caption(f'{fps:.0f}')
        else:
            pg.display.set_caption(f'{fps:.0f}')

    def render(self):
        # terrain chunks
        self.world.render()

        self.app.ctx.disable(mgl.CULL_FACE)

        # clouds only for non-cyberpunk scenes (dark sky looks better without)
        if self.app.terrain_type != TERRAIN_CYBERPUNK:
            self.clouds.render()

        self.water.render()

        # coloured-voxel objects (drones, hyperloops, fighters)
        for drone in self.drones:
            drone.render()
        for hl in self.hyperloops:
            hl.render()
        for bike in self.bikes:
            bike.render()
        for balloon in self.balloons:
            balloon.render()
        if self.dome:
            self.dome.render()

        self.app.ctx.enable(mgl.CULL_FACE)

        # voxel selection marker
        self.voxel_marker.render()
