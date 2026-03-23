# WASM build overrides — imported by main.py when running under Pygbag.
# Reduces world size so pure-Python mesh generation stays feasible in the browser.
import settings

# Smaller world for WASM (4x2x4 chunks instead of 20x2x20)
settings.WORLD_W = 4
settings.WORLD_D = settings.WORLD_W
settings.WORLD_AREA = settings.WORLD_W * settings.WORLD_D
settings.WORLD_VOL = settings.WORLD_AREA * settings.WORLD_H

# Smaller chunks for faster generation
settings.CHUNK_SIZE = 32
settings.H_CHUNK_SIZE = settings.CHUNK_SIZE // 2
settings.CHUNK_AREA = settings.CHUNK_SIZE * settings.CHUNK_SIZE
settings.CHUNK_VOL = settings.CHUNK_AREA * settings.CHUNK_SIZE

import math
settings.CHUNK_SPHERE_RADIUS = settings.H_CHUNK_SIZE * math.sqrt(3)

# Recalculate world center
settings.CENTER_XZ = settings.WORLD_W * settings.H_CHUNK_SIZE
settings.CENTER_Y = settings.WORLD_H * settings.H_CHUNK_SIZE

# Lower resolution for WASM
settings.WIN_RES = settings.glm.vec2(960, 540)
settings.ASPECT_RATIO = settings.WIN_RES.x / settings.WIN_RES.y

# Recalculate FOV
settings.V_FOV = settings.glm.radians(settings.FOV_DEG)
settings.H_FOV = 2 * math.atan(math.tan(settings.V_FOV * 0.5) * settings.ASPECT_RATIO)

# Recalculate player pos
settings.PLAYER_POS = settings.glm.vec3(
    settings.CENTER_XZ, settings.CHUNK_SIZE, settings.CENTER_XZ
)

# Water
settings.WATER_AREA = 5 * settings.CHUNK_SIZE * settings.WORLD_W

# WebGL 2 / OpenGL ES 3.0
settings.MAJOR_VER = 3
settings.MINOR_VER = 0
