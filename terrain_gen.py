from noise import noise2, noise3
from random import random
from settings import *


@njit
def get_height(x, z, terrain_type):
    # island mask (shared by all terrain types)
    island = 1 / (pow(0.0025 * math.hypot(x - CENTER_XZ, z - CENTER_XZ), 20) + 0.0001)
    island = min(island, 1)

    if terrain_type == 1:  # DESERT — flat sandy dunes
        a1 = CENTER_Y * 0.28
        f1 = 0.009
        f2 = f1 * 3
        height = 0.0
        height += noise2(x * f1, z * f1) * a1 + a1 * 0.35
        height += noise2(x * f2, z * f2) * a1 * 0.15
        height = max(height, 3.0)
        height *= island
        return int(height)

    if terrain_type == 2:  # FOREST — rolling hills carpeted with trees
        a1 = CENTER_Y * 0.45
        f1 = 0.007
        f2 = f1 * 2.5
        f4 = f1 * 5.0
        height = 0.0
        height += noise2(x * f1, z * f1) * a1 + a1 * 0.5
        height += noise2(x * f2, z * f2) * a1 * 0.25
        height += noise2(x * f4, z * f4) * a1 * 0.1
        height = max(height, 5.0)
        height *= island
        return int(height)

    a1 = CENTER_Y
    a2, a4, a8 = a1 * 0.5, a1 * 0.25, a1 * 0.125

    f1 = 0.005
    f2, f4, f8 = f1 * 2, f1 * 4, f1 * 8

    if noise2(0.1 * x, 0.1 * z) < 0:
        a1 /= 1.07

    height = 0
    height += noise2(x * f1, z * f1) * a1 + a1
    height += noise2(x * f2, z * f2) * a2 - a2
    height += noise2(x * f4, z * f4) * a4 + a4
    height += noise2(x * f8, z * f8) * a8 - a8

    height = max(height, noise2(x * f8, z * f8) + 2)
    height *= island

    return int(height)


@njit
def get_index(x, y, z):
    return x + CHUNK_SIZE * z + CHUNK_AREA * y


@njit
def set_voxel_id(voxels, x, y, z, wx, wy, wz, world_height, terrain_type):
    voxel_id = 0

    if terrain_type == 1:  # DESERT
        if wy < world_height - 1:
            # deep sand layer on top, stone below
            if wy >= world_height - 5:
                voxel_id = SAND
            else:
                voxel_id = STONE
        else:
            voxel_id = SAND
        voxels[get_index(x, y, z)] = voxel_id
        return

    if terrain_type == 2:  # FOREST
        if wy < world_height - 1:
            if (noise3(wx * 0.09, wy * 0.09, wz * 0.09) > 0 and
                    noise2(wx * 0.1, wz * 0.1) * 3 + 3 < wy < world_height - 8):
                voxel_id = 0
            elif wy >= world_height - 4:
                voxel_id = DIRT
            else:
                voxel_id = STONE
        else:
            voxel_id = GRASS
        voxels[get_index(x, y, z)] = voxel_id
        if wy < DIRT_LVL:
            place_forest_tree(voxels, x, y, z, voxel_id)
        return

    if wy < world_height - 1:
        # create caves
        if (noise3(wx * 0.09, wy * 0.09, wz * 0.09) > 0 and
                noise2(wx * 0.1, wz * 0.1) * 3 + 3 < wy < world_height - 10):
            voxel_id = 0

        else:
            voxel_id = STONE
    else:
        rng = int(7 * random())
        ry = wy - rng
        if SNOW_LVL <= ry < world_height:
            voxel_id = SNOW

        elif STONE_LVL <= ry < SNOW_LVL:
            voxel_id = STONE

        elif DIRT_LVL <= ry < STONE_LVL:
            voxel_id = DIRT

        elif GRASS_LVL <= ry < DIRT_LVL:
            voxel_id = GRASS

        else:
            voxel_id = SAND

    # setting ID
    voxels[get_index(x, y, z)] = voxel_id

    # place tree
    if wy < DIRT_LVL:
        place_tree(voxels, x, y, z, voxel_id)


@njit
def place_oak_tree(voxels, x, y, z):
    """Classic oak: rounded canopy, short trunk."""
    if y + TREE_HEIGHT >= CHUNK_SIZE:
        return None
    if x - TREE_H_WIDTH < 0 or x + TREE_H_WIDTH >= CHUNK_SIZE:
        return None
    if z - TREE_H_WIDTH < 0 or z + TREE_H_WIDTH >= CHUNK_SIZE:
        return None

    voxels[get_index(x, y, z)] = DIRT

    m = 0
    for n, iy in enumerate(range(TREE_H_HEIGHT, TREE_HEIGHT - 1)):
        k = iy % 2
        rng = int(random() * 2)
        for ix in range(-TREE_H_WIDTH + m, TREE_H_WIDTH - m * rng):
            for iz in range(-TREE_H_WIDTH + m * rng, TREE_H_WIDTH - m):
                if (ix + iz) % 4:
                    voxels[get_index(x + ix + k, y + iy, z + iz + k)] = LEAVES
        m += 1 if n > 0 else 3 if n > 1 else 0

    for iy in range(1, TREE_HEIGHT - 2):
        voxels[get_index(x, y + iy, z)] = WOOD

    voxels[get_index(x, y + TREE_HEIGHT - 2, z)] = LEAVES


@njit
def place_pine(voxels, x, y, z):
    """Large conical pine: tall WOOD trunk, tiered LEAVES rings narrowing upward."""
    if y + 14 >= CHUNK_SIZE:
        return None
    if x - 2 < 0 or x + 2 >= CHUNK_SIZE:
        return None
    if z - 2 < 0 or z + 2 >= CHUNK_SIZE:
        return None

    voxels[get_index(x, y, z)] = DIRT

    for iy in range(1, 13):
        voxels[get_index(x, y + iy, z)] = WOOD

    # wide layers at base, narrowing toward tip
    for ix in range(-2, 3):
        for iz in range(-2, 3):
            voxels[get_index(x + ix, y + 2, z + iz)] = LEAVES
    for ix in range(-2, 3):
        for iz in range(-2, 3):
            voxels[get_index(x + ix, y + 4, z + iz)] = LEAVES
    for ix in range(-2, 3):
        for iz in range(-2, 3):
            if ix * ix + iz * iz <= 5:
                voxels[get_index(x + ix, y + 6, z + iz)] = LEAVES
    for ix in range(-1, 2):
        for iz in range(-1, 2):
            voxels[get_index(x + ix, y + 8, z + iz)] = LEAVES
    for ix in range(-1, 2):
        for iz in range(-1, 2):
            voxels[get_index(x + ix, y + 10, z + iz)] = LEAVES
    for ix in range(-1, 2):
        for iz in range(-1, 2):
            voxels[get_index(x + ix, y + 12, z + iz)] = LEAVES
    voxels[get_index(x, y + 13, z)] = LEAVES


@njit
def place_shrub(voxels, x, y, z):
    """Dense low shrub: compact 3x3 LEAVES blob, no visible trunk."""
    if y + 3 >= CHUNK_SIZE:
        return None
    if x - 1 < 0 or x + 1 >= CHUNK_SIZE:
        return None
    if z - 1 < 0 or z + 1 >= CHUNK_SIZE:
        return None

    for ix in range(-1, 2):
        for iz in range(-1, 2):
            voxels[get_index(x + ix, y + 1, z + iz)] = LEAVES
    voxels[get_index(x, y + 2, z)] = LEAVES


@njit
def place_mushroom(voxels, x, y, z):
    """Mushroom: thin WOOD stem, DIRT under-cap, wide SAND dome cap."""
    if y + 7 >= CHUNK_SIZE:
        return None
    if x - 2 < 0 or x + 2 >= CHUNK_SIZE:
        return None
    if z - 2 < 0 or z + 2 >= CHUNK_SIZE:
        return None

    for iy in range(1, 4):
        voxels[get_index(x, y + iy, z)] = WOOD

    # under-cap fringe
    for ix in range(-1, 2):
        for iz in range(-1, 2):
            voxels[get_index(x + ix, y + 4, z + iz)] = DIRT

    # wide brim
    for ix in range(-2, 3):
        for iz in range(-2, 3):
            if abs(ix) + abs(iz) <= 3:
                voxels[get_index(x + ix, y + 5, z + iz)] = SAND

    # dome top
    for ix in range(-1, 2):
        for iz in range(-1, 2):
            voxels[get_index(x + ix, y + 6, z + iz)] = SAND


@njit
def place_bamboo(voxels, x, y, z):
    """Bamboo: single-column WOOD stalk, small LEAVES tuft at the crown."""
    if y + 11 >= CHUNK_SIZE:
        return None
    if x - 1 < 0 or x + 1 >= CHUNK_SIZE:
        return None
    if z - 1 < 0 or z + 1 >= CHUNK_SIZE:
        return None

    for iy in range(1, 10):
        voxels[get_index(x, y + iy, z)] = WOOD

    for ix in range(-1, 2):
        for iz in range(-1, 2):
            voxels[get_index(x + ix, y + 9, z + iz)] = LEAVES
    voxels[get_index(x, y + 10, z)] = LEAVES


@njit
def place_palash(voxels, x, y, z):
    """Palash (flame of the forest): LEAVES canopy dotted with SNOW flower-blocks."""
    if y + 9 >= CHUNK_SIZE:
        return None
    if x - 2 < 0 or x + 2 >= CHUNK_SIZE:
        return None
    if z - 2 < 0 or z + 2 >= CHUNK_SIZE:
        return None

    voxels[get_index(x, y, z)] = DIRT

    for iy in range(1, 6):
        voxels[get_index(x, y + iy, z)] = WOOD

    # lower canopy: mostly LEAVES
    for ix in range(-2, 3):
        for iz in range(-2, 3):
            voxels[get_index(x + ix, y + 5, z + iz)] = LEAVES

    # mid canopy: LEAVES mixed with SNOW flowers
    for ix in range(-2, 3):
        for iz in range(-2, 3):
            flower = (ix + iz + int(random() * 3)) % 2 == 0
            voxels[get_index(x + ix, y + 6, z + iz)] = SNOW if flower else LEAVES

    # upper bloom: mostly SNOW
    for ix in range(-1, 2):
        for iz in range(-1, 2):
            voxels[get_index(x + ix, y + 7, z + iz)] = SNOW

    voxels[get_index(x, y + 8, z)] = SNOW


@njit
def place_tree(voxels, x, y, z, voxel_id):
    """Grassland dispatcher: oaks (65%), pines (20%), bamboo (15%)."""
    rnd = random()
    if voxel_id != GRASS or rnd > TREE_PROBABILITY:
        return None
    t = random()
    if t < 0.65:
        place_oak_tree(voxels, x, y, z)
    elif t < 0.85:
        place_pine(voxels, x, y, z)
    else:
        place_bamboo(voxels, x, y, z)


@njit
def place_forest_tree(voxels, x, y, z, voxel_id):
    """Forest dispatcher: pines (25%), shrubs (20%), mushrooms (15%), bamboo (15%), palash (25%)."""
    rnd = random()
    if voxel_id != GRASS or rnd > FOREST_TREE_PROBABILITY:
        return None
    t = random()
    if t < 0.25:
        place_pine(voxels, x, y, z)
    elif t < 0.45:
        place_shrub(voxels, x, y, z)
    elif t < 0.60:
        place_mushroom(voxels, x, y, z)
    elif t < 0.75:
        place_bamboo(voxels, x, y, z)
    else:
        place_palash(voxels, x, y, z)
