import math
import random

from settings import *
from meshes.voxel_body_mesh import VoxelBodyMesh


# ---------------------------------------------------------------------------
# Neon bike colour palettes  (body dark metal, neon trim + wheels)
# ---------------------------------------------------------------------------
_PALETTES = [
    {'body': (0.08, 0.08, 0.12), 'trim': (0.00, 1.00, 0.90), 'wheel': (0.05, 0.60, 0.70)},  # cyan
    {'body': (0.12, 0.04, 0.12), 'trim': (1.00, 0.05, 0.75), 'wheel': (0.70, 0.03, 0.50)},  # magenta
    {'body': (0.04, 0.12, 0.06), 'trim': (0.10, 1.00, 0.20), 'wheel': (0.06, 0.65, 0.14)},  # green
    {'body': (0.12, 0.09, 0.02), 'trim': (1.00, 0.55, 0.00), 'wheel': (0.80, 0.35, 0.00)},  # orange
]


def _make_bike_voxels(palette):
    """
    Side-view of a sleek 9-voxel motorbike (facing +Z):

        y=2  . . H . .    cockpit / rider silhouette
        y=1  F B B B R    front-fork, body ×3, rear
        y=0  W . . . W    front wheel, rear wheel

    Widened by 1 block on each side at body level for bulk.
    """
    b = palette['body']
    t = palette['trim']
    w = palette['wheel']
    return [
        # wheels (neon rim)
        ( 0, 0,  0, *w),  # front wheel
        ( 0, 0,  4, *w),  # rear wheel
        # body row
        ( 0, 1,  0, *t),  # front fork (neon)
        ( 0, 1,  1, *b),  # body
        (-1, 1,  2, *b),  ( 0, 1, 2, *b),  (1, 1, 2, *b),  # wide mid-body
        ( 0, 1,  3, *b),  # body
        ( 0, 1,  4, *t),  # tail light (neon)
        # cockpit / rider
        ( 0, 2,  2, *t),  # rider torso / handlebar neon
    ]


class Bike:
    """
    A neon voxel motorbike that races along a straight road lane,
    looping back when it reaches the far end.
    """

    def __init__(self, app, position, palette_idx=0,
                 speed=18.0, axis='x', lane_length=150):
        self.app         = app
        self.speed       = speed
        self.axis        = axis          # 'x' or 'z'
        self.lane_length = lane_length
        self.t           = random.uniform(0.0, lane_length)   # start at random point

        pal = _PALETTES[palette_idx % len(_PALETTES)]
        self.mesh     = VoxelBodyMesh(app, _make_bike_voxels(pal))
        self._origin  = glm.vec3(position)
        self.position = glm.vec3(position)
        self.m_model  = self._build_model()

    # ------------------------------------------------------------------
    def update(self, dt: float):
        self.t = (self.t + self.speed * dt) % self.lane_length

        if self.axis == 'x':
            self.position = glm.vec3(
                self._origin.x + self.t,
                self._origin.y,
                self._origin.z
            )
            yaw = 0.0
        else:
            self.position = glm.vec3(
                self._origin.x,
                self._origin.y,
                self._origin.z + self.t
            )
            yaw = math.pi * 0.5

        self.m_model = self._build_model(yaw)

    def render(self):
        self.mesh.program['m_model'].write(self.m_model)
        self.mesh.render()

    # ------------------------------------------------------------------
    def _build_model(self, yaw=0.0):
        m = glm.translate(glm.mat4(), self.position)
        m = glm.rotate(m, yaw, glm.vec3(0, 1, 0))
        return m
