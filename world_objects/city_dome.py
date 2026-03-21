import math
from settings import *
from meshes.voxel_body_mesh import VoxelBodyMesh

# ---------------------------------------------------------------------------
# Colour palette — ice-blue glass, dark steel frame, neon trim, forest floor
# ---------------------------------------------------------------------------
_GLASS  = (0.82, 0.94, 1.00)   # pale glass panels
_FRAME  = (0.14, 0.16, 0.24)   # dark steel gridwork
_NEON_C = (0.00, 0.90, 1.00)   # cyan LED base ring
_NEON_M = (0.95, 0.05, 0.80)   # magenta mid-height accent band
_FOREST = (0.12, 0.70, 0.22)   # interior planting / forest floor
_PILLAR = (0.08, 0.50, 0.16)   # ornamental tree-column


def _build_dome_voxels(outer_r: int = 22,
                       inner_r: int = 8,
                       dome_h:  int = 14):
    """
    Procedurally generate a Jewel-Changi-style torus dome:

    • Arching glass-and-steel roof shell over a ring-shaped plan.
    • Central void (Rain Vortex atrium) left open.
    • Cyan neon LED strip at ground level, magenta band at mid-span.
    • Interior forest floor with ornamental greenery columns.

    The structure is centred at the origin; translate via m_model.
    """
    ring_r = (outer_r + inner_r) / 2.0   # centreline radius of the annulus
    half_w = (outer_r - inner_r) / 2.0   # half-width of ring

    voxels: list = []
    seen:   set  = set()

    def _add(x, y, z, col):
        k = (x, y, z)
        if k not in seen:
            seen.add(k)
            voxels.append((x, y, z, *col))

    for ix in range(-(outer_r + 2), outer_r + 3):
        for iz in range(-(outer_r + 2), outer_r + 3):
            r  = math.sqrt(ix * ix + iz * iz)
            dr = r - ring_r

            # dome surface height at this xz position (torus-dome profile)
            if abs(dr) <= half_w:
                surf_h = dome_h * math.sqrt(1.0 - (dr / half_w) ** 2)
            else:
                surf_h = 0.0

            ih = max(0, int(surf_h + 0.5))   # rounded height

            # ── Glass roof shell (1–2 voxels thick at the surface) ──
            if inner_r - 0.5 <= r <= outer_r + 0.5 and ih >= 1:
                for dy in range(max(1, ih - 1), ih + 2):
                    # steel grid lines every 4 blocks; glass elsewhere
                    is_frame = (ix % 4 == 0) or (iz % 4 == 0)
                    _add(ix, dy, iz, _FRAME if is_frame else _GLASS)

            # ── Outer base curtain wall (3 voxels tall) ──
            if outer_r - 0.7 <= r <= outer_r + 0.7:
                for iy in range(0, 4):
                    _add(ix, iy, iz, _FRAME)
                # cyan neon strip inset at base (y = -1 sits on the ground plane)
                _add(ix, -1, iz, _NEON_C)

            # ── Magenta neon band at mid-span ──
            if outer_r - 0.7 <= r <= outer_r + 0.7 and ih >= 6:
                _add(ix, max(3, ih // 2), iz, _NEON_M)

            # ── Interior forest floor ──
            if inner_r + 0.5 < r < outer_r - 0.5:
                _add(ix, 0, iz, _FOREST)
                # ornamental tree pillars on a 5-block grid
                if (abs(ix) % 5 == 2) and (abs(iz) % 5 == 2):
                    for iy in range(1, 6):
                        _add(ix, iy, iz, _PILLAR)
                    # canopy top
                    for dix in range(-1, 2):
                        for diz in range(-1, 2):
                            _add(ix + dix, 6, iz + diz, _FOREST)

    return voxels


class CityDome:
    """
    A landmark Jewel Changi-inspired glass torus dome placed in the
    cyberpunk city.  It is purely static — no update() is needed.
    """

    def __init__(self, app, position):
        self.app     = app
        voxels       = _build_dome_voxels()
        self.mesh    = VoxelBodyMesh(app, voxels)
        self.m_model = glm.translate(glm.mat4(), glm.vec3(position))

    def render(self):
        self.mesh.program['m_model'].write(self.m_model)
        self.mesh.render()
