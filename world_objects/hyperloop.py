from settings import *
from meshes.voxel_body_mesh import VoxelBodyMesh


# ---------------------------------------------------------------------------
# Two colour schemes – one per hyperloop line
# ---------------------------------------------------------------------------
_SCHEMES = [
    {'tube': (0.00, 0.85, 1.00), 'support': (0.20, 0.22, 0.35)},   # cyan line
    {'tube': (1.00, 0.10, 0.65), 'support': (0.35, 0.18, 0.28)},   # magenta line
]

# Hollow 3 × 3 cross-section (8 voxels, centre empty)
#   T T T
#   T . T
#   T T T
_CROSS = [
    (-1, 0), (0, 0), (1, 0),   # bottom row
    (-1, 1),          (1, 1),  # middle row sides
    (-1, 2), (0, 2), (1, 2),   # top row
]

_SUPPORT_INTERVAL = 15   # blocks between support pillars
_PILLAR_DEPTH     = 14   # how many voxels downward each pillar extends


def _build_hyperloop_voxels(length: int, scheme: dict, axis: str):
    """
    Build a hollow rectangular tube of *length* voxels along *axis* ('x' or 'z'),
    with support pillars every _SUPPORT_INTERVAL steps.

    The tube's bottom-left-front corner sits at (0,0,0) in model space.
    """
    tube = scheme['tube']
    sup  = scheme['support']
    voxels = []

    for i in range(length):
        # tube cross-section
        for (a, b) in _CROSS:
            if axis == 'x':
                voxels.append((i, b, a, *tube))
            else:
                voxels.append((a, b, i, *tube))

        # support pillar (down from  y = -1)
        if i % _SUPPORT_INTERVAL == _SUPPORT_INTERVAL // 2:
            for ph in range(1, _PILLAR_DEPTH + 1):
                if axis == 'x':
                    voxels.append((i, -ph, 0, *sup))
                else:
                    voxels.append((0, -ph, i, *sup))

    return voxels


class Hyperloop:
    """
    A static elevated transit tube made of coloured voxels.
    Two instances (cyan east-west / magenta north-south) cross at the
    city centre to form the signature Cyberpunk hyperloop interchange.
    """

    def __init__(self, app, position, length: int = 160,
                 color_idx: int = 0, axis: str = 'x'):
        self.app = app
        scheme   = _SCHEMES[color_idx % len(_SCHEMES)]
        voxels   = _build_hyperloop_voxels(length, scheme, axis)

        self.mesh    = VoxelBodyMesh(app, voxels)
        self.m_model = glm.translate(glm.mat4(), glm.vec3(position))

    def render(self):
        self.mesh.program['m_model'].write(self.m_model)
        self.mesh.render()
