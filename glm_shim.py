"""
Lightweight GLM shim for environments where PyGLM is unavailable (e.g. WASM).
Provides only the subset used by this project.
"""
import math
import struct


class vec2:
    __slots__ = ('x', 'y')

    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)

    def __iter__(self):
        yield self.x
        yield self.y


class vec3:
    __slots__ = ('x', 'y', 'z')

    def __init__(self, x=0.0, y=0.0, z=0.0):
        if isinstance(x, (tuple, list)):
            self.x, self.y, self.z = float(x[0]), float(x[1]), float(x[2])
        elif isinstance(x, vec3):
            self.x, self.y, self.z = x.x, x.y, x.z
        else:
            self.x = float(x)
            self.y = float(y)
            self.z = float(z)

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return vec3(self.x + other, self.y + other, self.z + other)
        return vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return vec3(self.x - other, self.y - other, self.z - other)
        return vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __rsub__(self, other):
        if isinstance(other, (int, float)):
            return vec3(other - self.x, other - self.y, other - self.z)
        return vec3(other.x - self.x, other.y - self.y, other.z - self.z)

    def __mul__(self, s):
        if isinstance(s, (int, float)):
            return vec3(self.x * s, self.y * s, self.z * s)
        return vec3(self.x * s.x, self.y * s.y, self.z * s.z)

    def __rmul__(self, s):
        return self.__mul__(s)

    def __neg__(self):
        return vec3(-self.x, -self.y, -self.z)

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    def __repr__(self):
        return f'vec3({self.x}, {self.y}, {self.z})'


class ivec3:
    __slots__ = ('x', 'y', 'z')

    def __init__(self, x=0, y=0, z=0):
        if isinstance(x, (tuple, list)):
            self.x, self.y, self.z = int(x[0]), int(x[1]), int(x[2])
        elif isinstance(x, (vec3, ivec3)):
            self.x, self.y, self.z = int(x.x), int(x.y), int(x.z)
        else:
            self.x = int(x)
            self.y = int(y)
            self.z = int(z)

    def __mul__(self, s):
        return ivec3(self.x * s, self.y * s, self.z * s)

    def __rmul__(self, s):
        return self.__mul__(s)

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z


def dot(a, b):
    return a.x * b.x + a.y * b.y + a.z * b.z


def cross(a, b):
    return vec3(
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x,
    )


def normalize(v):
    length = math.sqrt(v.x * v.x + v.y * v.y + v.z * v.z)
    if length < 1e-12:
        return vec3(0, 0, 0)
    return vec3(v.x / length, v.y / length, v.z / length)


def cos(x):
    return math.cos(x)


def sin(x):
    return math.sin(x)


def clamp(x, lo, hi):
    return max(lo, min(x, hi))


class mat4:
    """Column-major 4x4 matrix stored as a flat list of 16 floats."""

    def __init__(self, *args):
        if len(args) == 0:
            self.data = [
                1, 0, 0, 0,
                0, 1, 0, 0,
                0, 0, 1, 0,
                0, 0, 0, 1,
            ]
        elif len(args) == 16:
            self.data = [float(x) for x in args]
        elif len(args) == 1 and hasattr(args[0], 'data'):
            self.data = list(args[0].data)
        else:
            self.data = [
                1, 0, 0, 0,
                0, 1, 0, 0,
                0, 0, 1, 0,
                0, 0, 0, 1,
            ]

    def __matmul__(self, other):
        a, b = self.data, other.data
        r = [0.0] * 16
        for col in range(4):
            for row in range(4):
                s = 0.0
                for k in range(4):
                    s += a[k * 4 + row] * b[col * 4 + k]
                r[col * 4 + row] = s
        m = mat4()
        m.data = r
        return m

    def write(self):
        """Return bytes suitable for moderngl uniform writes."""
        return struct.pack('16f', *self.data)


def translate(m, v):
    result = mat4()
    result.data = list(m.data)
    result.data[12] = m.data[0] * v.x + m.data[4] * v.y + m.data[8] * v.z + m.data[12]
    result.data[13] = m.data[1] * v.x + m.data[5] * v.y + m.data[9] * v.z + m.data[13]
    result.data[14] = m.data[2] * v.x + m.data[6] * v.y + m.data[10] * v.z + m.data[14]
    result.data[15] = m.data[3] * v.x + m.data[7] * v.y + m.data[11] * v.z + m.data[15]
    return result


def radians(deg):
    return math.radians(deg)


def perspective(fov, aspect, near, far):
    f = 1.0 / math.tan(fov / 2.0)
    m = mat4()
    m.data = [0.0] * 16
    m.data[0] = f / aspect
    m.data[5] = f
    m.data[10] = (far + near) / (near - far)
    m.data[11] = -1.0
    m.data[14] = (2.0 * far * near) / (near - far)
    return m


def lookAt(eye, center, up):
    f = normalize(vec3(center.x - eye.x, center.y - eye.y, center.z - eye.z))
    s = normalize(cross(f, up))
    u = cross(s, f)

    m = mat4()
    m.data[0] = s.x;  m.data[4] = s.y;  m.data[8]  = s.z
    m.data[1] = u.x;  m.data[5] = u.y;  m.data[9]  = u.z
    m.data[2] = -f.x; m.data[6] = -f.y; m.data[10] = -f.z
    m.data[12] = -dot(s, eye)
    m.data[13] = -dot(u, eye)
    m.data[14] = dot(f, eye)
    m.data[15] = 1.0
    return m


# expose as module-like so `from glm_shim import glm` works
class _GlmModule:
    vec2 = vec2
    vec3 = vec3
    ivec3 = ivec3
    mat4 = mat4
    radians = staticmethod(radians)
    perspective = staticmethod(perspective)
    lookAt = staticmethod(lookAt)
    normalize = staticmethod(normalize)
    cross = staticmethod(cross)
    dot = staticmethod(dot)
    cos = staticmethod(cos)
    sin = staticmethod(sin)
    clamp = staticmethod(clamp)
    translate = staticmethod(translate)


glm = _GlmModule()
