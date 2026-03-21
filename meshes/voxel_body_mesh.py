import numpy as np
from meshes.base_mesh import BaseMesh

# ---------------------------------------------------------------------------
# Each cube face: (neighbor_offset, corner_offsets_for_4_verts, shading)
# corner offsets are (fx, fy, fz) relative to the block's min-corner (ix,iy,iz)
# shading simulates a simple directional light without a real normal buffer
# ---------------------------------------------------------------------------
CUBE_FACES = [
    # Top    (+Y)
    (( 0,  1,  0), [(0,1,0),(1,1,0),(1,1,1),(0,1,1)], 1.00),
    # Bottom (-Y)
    (( 0, -1,  0), [(0,0,1),(1,0,1),(1,0,0),(0,0,0)], 0.45),
    # Right  (+X)
    (( 1,  0,  0), [(1,0,0),(1,1,0),(1,1,1),(1,0,1)], 0.85),
    # Left   (-X)
    ((-1,  0,  0), [(0,0,1),(0,1,1),(0,1,0),(0,0,0)], 0.60),
    # Front  (+Z)
    (( 0,  0,  1), [(0,0,1),(1,0,1),(1,1,1),(0,1,1)], 0.80),
    # Back   (-Z)
    (( 0,  0, -1), [(1,0,0),(0,0,0),(0,1,0),(1,1,0)], 0.65),
]

# Each face → 2 triangles (CCW, but we render with CULL_FACE disabled anyway)
_TRIS = ((0, 1, 2), (0, 2, 3))


def build_voxel_mesh_data(voxels):
    """
    Build a flat float32 vertex buffer for a list of coloured voxel blocks.

    Parameters
    ----------
    voxels : list of (ix, iy, iz, r, g, b)
        Integer block grid coordinates and RGB colour (0-1 float).
        The mesh is centred on X/Z so that a block at ix=0 occupies
        x = [-0.5, 0.5] and z = [-0.5, 0.5].
        Y is not shifted – feet are at y = 0.

    Returns
    -------
    numpy.ndarray  dtype='f4', shape (N*7,)
        Packed as: [x, y, z, r, g, b, shading] per vertex.
    """
    voxel_set = {(int(v[0]), int(v[1]), int(v[2])) for v in voxels}
    buf = []

    for ix, iy, iz, r, g, b in voxels:
        ixi, iyi, izi = int(ix), int(iy), int(iz)

        for (ndx, ndy, ndz), fv, shading in CUBE_FACES:
            # skip faces shared with an adjacent voxel (hidden face removal)
            if (ixi + ndx, iyi + ndy, izi + ndz) in voxel_set:
                continue

            # compute 4 corner positions (centering offset: -0.5 on X and Z)
            corners = [
                (ixi + fx - 0.5, iyi + fy, izi + fz - 0.5)
                for fx, fy, fz in fv
            ]

            for tri in _TRIS:
                for vi in tri:
                    cx, cy, cz = corners[vi]
                    buf += [cx, cy, cz, r, g, b, shading]

    if not buf:
        return np.zeros(7, dtype='f4')
    return np.array(buf, dtype='f4')


class VoxelBodyMesh(BaseMesh):
    """
    A static GPU mesh built from a list of coloured unit-cube voxels.
    Used to render the two AI fighter characters.
    """

    def __init__(self, app, voxels):
        super().__init__()
        self.app     = app
        self.ctx     = app.ctx
        self.program = app.shader_program.player_entity
        self.voxels  = voxels

        # layout: 3 floats position | 3 floats colour | 1 float shading
        self.vbo_format = '3f 3f 1f'
        self.attrs      = ('in_position', 'in_color', 'in_shading')
        self.vao        = self.get_vao()

    def get_vertex_data(self):
        return build_voxel_mesh_data(self.voxels)
