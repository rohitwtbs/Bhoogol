import math
import random

from settings import *
from meshes.voxel_body_mesh import VoxelBodyMesh


# Balloon body colour options (vivid RGB, each 8-voxel sphere-ish blob)
_BALLOON_COLORS = [
    (1.00, 0.05, 0.30),   # hot pink
    (0.00, 0.85, 1.00),   # cyan
    (0.90, 0.50, 0.00),   # amber
    (0.55, 0.00, 1.00),   # violet
    (0.10, 1.00, 0.40),   # lime
    (1.00, 0.20, 0.00),   # red-orange
]

_BASKET_COLOR  = (0.45, 0.30, 0.10)   # wicker brown
_ROPE_COLOR    = (0.70, 0.65, 0.40)   # rope tan


def _make_balloon_voxels(color):
    """
    Voxel hot-air balloon (centred at origin, basket hangs below):

        y=6        B          top cap
        y=5     B  B  B       upper band
        y=4  B  B  B  B  B   equator (widest)
        y=3     B  B  B       lower band
        y=2        B          base cap
        y=1        R          rope
        y=0     [bbb]         basket (3 wide)
    """
    c = color
    b = _BASKET_COLOR
    r = _ROPE_COLOR
    return [
        # balloon envelope
        ( 0, 6,  0, *c),
        (-1, 5,  0, *c), (0, 5,  0, *c), (1, 5,  0, *c),
        ( 0, 5, -1, *c), (0, 5,  1, *c),
        (-2, 4,  0, *c), (-1, 4,  0, *c), (0, 4, 0, *c), (1, 4, 0, *c), (2, 4, 0, *c),
        ( 0, 4, -1, *c), ( 0, 4,  1, *c),
        (-1, 3,  0, *c), ( 0, 3,  0, *c), (1, 3,  0, *c),
        ( 0, 3, -1, *c), ( 0, 3,  1, *c),
        ( 0, 2,  0, *c),
        # rope
        ( 0, 1,  0, *r),
        # basket
        (-1, 0,  0, *b), (0, 0, 0, *b), (1, 0, 0, *b),
        ( 0, 0, -1, *b), (0, 0, 1, *b),
    ]


class HotAirBalloon:
    """
    A colourful voxel hot-air balloon that drifts slowly across the sky,
    gently bobbing up and down.
    """

    def __init__(self, app, position, color_idx=0, drift_speed=1.5, axis='x'):
        self.app         = app
        self.drift_speed = drift_speed
        self.axis        = axis
        self.bob_t       = random.uniform(0.0, math.tau)
        self.drift_t     = random.uniform(0.0, 300.0)
        self.drift_range = 180.0     # blocks to drift before looping

        color = _BALLOON_COLORS[color_idx % len(_BALLOON_COLORS)]
        self.mesh    = VoxelBodyMesh(app, _make_balloon_voxels(color))
        self._origin = glm.vec3(position)
        self.position = glm.vec3(position)
        self.m_model = self._build_model()

    # ------------------------------------------------------------------
    def update(self, dt: float):
        self.drift_t = (self.drift_t + self.drift_speed * dt) % self.drift_range
        self.bob_t  += 0.5 * dt

        bob_y = math.sin(self.bob_t) * 3.0

        if self.axis == 'x':
            self.position = glm.vec3(
                self._origin.x + self.drift_t,
                self._origin.y + bob_y,
                self._origin.z
            )
        else:
            self.position = glm.vec3(
                self._origin.x,
                self._origin.y + bob_y,
                self._origin.z + self.drift_t
            )

        self.m_model = self._build_model()

    def render(self):
        self.mesh.program['m_model'].write(self.m_model)
        self.mesh.render()

    # ------------------------------------------------------------------
    def _build_model(self):
        return glm.translate(glm.mat4(), self.position)
