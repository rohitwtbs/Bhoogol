"""
Minimal opensimplex shim for WASM environments.
Provides _init, _noise2, _noise3 using basic value-noise when the native
opensimplex C extension is unavailable.  Not identical output but generates
plausible terrain.
"""
import math
import numpy as np


def _init(seed=0):
    rng = np.random.RandomState(seed)
    perm = np.arange(256, dtype='int32')
    rng.shuffle(perm)
    perm = np.concatenate([perm, perm])
    perm_grad_index3 = (perm % 12).astype('int32')
    return perm, perm_grad_index3


_GRAD3 = [
    (1, 1, 0), (-1, 1, 0), (1, -1, 0), (-1, -1, 0),
    (1, 0, 1), (-1, 0, 1), (1, 0, -1), (-1, 0, -1),
    (0, 1, 1), (0, -1, 1), (0, 1, -1), (0, -1, -1),
]


def _fade(t):
    return t * t * t * (t * (t * 6 - 15) + 10)


def _lerp(a, b, t):
    return a + t * (b - a)


def _grad2(h, x, y):
    g = _GRAD3[h % 12]
    return g[0] * x + g[1] * y


def _grad3(h, x, y, z):
    g = _GRAD3[h % 12]
    return g[0] * x + g[1] * y + g[2] * z


def _noise2(x, y, perm):
    X = int(math.floor(x)) & 255
    Y = int(math.floor(y)) & 255
    x -= math.floor(x)
    y -= math.floor(y)
    u = _fade(x)
    v = _fade(y)

    A = perm[X] + Y
    B = perm[X + 1] + Y

    return _lerp(
        _lerp(_grad2(perm[A], x, y), _grad2(perm[B], x - 1, y), u),
        _lerp(_grad2(perm[A + 1], x, y - 1), _grad2(perm[B + 1], x - 1, y - 1), u),
        v
    )


def _noise3(x, y, z, perm, perm_grad_index3):
    X = int(math.floor(x)) & 255
    Y = int(math.floor(y)) & 255
    Z = int(math.floor(z)) & 255
    x -= math.floor(x)
    y -= math.floor(y)
    z -= math.floor(z)
    u = _fade(x)
    v = _fade(y)
    w = _fade(z)

    A = perm[X] + Y
    AA = perm[A] + Z
    AB = perm[A + 1] + Z
    B = perm[X + 1] + Y
    BA = perm[B] + Z
    BB = perm[B + 1] + Z

    return _lerp(
        _lerp(
            _lerp(_grad3(perm[AA], x, y, z), _grad3(perm[BA], x - 1, y, z), u),
            _lerp(_grad3(perm[AB], x, y - 1, z), _grad3(perm[BB], x - 1, y - 1, z), u),
            v
        ),
        _lerp(
            _lerp(_grad3(perm[AA + 1], x, y, z - 1), _grad3(perm[BA + 1], x - 1, y, z - 1), u),
            _lerp(_grad3(perm[AB + 1], x, y - 1, z - 1), _grad3(perm[BB + 1], x - 1, y - 1, z - 1), u),
            v
        ),
        w
    )
