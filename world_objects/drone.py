import math
import random

from settings import *
from meshes.voxel_body_mesh import VoxelBodyMesh


# ---------------------------------------------------------------------------
# Neon colour palettes – body is dark metal, arms glow in different hues
# ---------------------------------------------------------------------------
_PALETTES = [
    {'body': (0.10, 0.10, 0.15), 'arm': (0.00, 0.90, 1.00)},   # cyan
    {'body': (0.12, 0.05, 0.15), 'arm': (1.00, 0.05, 0.80)},   # magenta
    {'body': (0.05, 0.15, 0.08), 'arm': (0.10, 1.00, 0.30)},   # green
    {'body': (0.15, 0.10, 0.02), 'arm': (1.00, 0.60, 0.00)},   # orange
    {'body': (0.08, 0.04, 0.18), 'arm': (0.60, 0.10, 1.00)},   # violet
    {'body': (0.02, 0.12, 0.18), 'arm': (0.00, 0.70, 1.00)},   # sky-blue
]


def _make_drone_voxels(palette):
    """
    X-shaped drone (top-down):

        . A . A .    y=0  arm tips (neon)
        A . C . A    y=0  arms + core
        . A . A .    y=0  arm tips (neon)
        . . C . .    y=-1 underbody

    Flattened to a 10-voxel layout for a clean X rotor silhouette.
    """
    b = palette['body']
    a = palette['arm']
    return [
        # body core
        ( 0,  1,  0, *b),   # top sensor dome
        ( 0,  0,  0, *b),   # central body
        ( 0, -1,  0, *b),   # underbody
        # four rotor arms (neon)
        (-1,  0,  0, *a),
        ( 1,  0,  0, *a),
        ( 0,  0, -1, *a),
        ( 0,  0,  1, *a),
        # rotor tips (neon, one voxel further out)
        (-2,  0,  0, *a),
        ( 2,  0,  0, *a),
        ( 0,  0, -2, *a),
        ( 0,  0,  2, *a),
    ]


class Drone:
    """
    A small neon-coloured voxel drone that orbits a centre point in a
    smooth circle while bobbing up and down.  Multiple drones with
    different radii / heights give the feel of a busy air-traffic lane.
    """

    def __init__(self, app, position, palette_idx=0,
                 patrol_radius=16.0, speed=1.0):
        self.app    = app
        pal         = _PALETTES[palette_idx % len(_PALETTES)]
        self.speed  = speed
        self.radius = patrol_radius
        self.center = glm.vec3(position)
        self.angle  = random.uniform(0.0, 2.0 * math.pi)
        self.bob_t  = random.uniform(0.0, 2.0 * math.pi)

        self.position = glm.vec3(position)
        self.mesh     = VoxelBodyMesh(app, _make_drone_voxels(pal))
        self.m_model  = self._build_model()

    # ------------------------------------------------------------------
    def update(self, dt: float):
        self.angle += self.speed * dt
        self.bob_t += 1.4 * dt

        x = self.center.x + math.cos(self.angle) * self.radius
        z = self.center.z + math.sin(self.angle) * self.radius
        y = self.center.y + math.sin(self.bob_t) * 2.0

        self.position = glm.vec3(x, y, z)
        self.m_model  = self._build_model()

    def render(self):
        self.mesh.program['m_model'].write(self.m_model)
        self.mesh.render()

    # ------------------------------------------------------------------
    def _build_model(self):
        m = glm.translate(glm.mat4(), self.position)
        # face direction of travel
        m = glm.rotate(m, self.angle + math.pi * 0.5, glm.vec3(0.0, 1.0, 0.0))
        m = glm.scale(m, glm.vec3(0.55))
        return m
