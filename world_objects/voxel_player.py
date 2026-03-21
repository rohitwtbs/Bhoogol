import math
import random

from settings import *
from meshes.voxel_body_mesh import VoxelBodyMesh
from terrain_gen import get_height


# ---------------------------------------------------------------------------
# Colour schemes: two fighters with distinct armour colours
# ---------------------------------------------------------------------------
_SCHEMES = {
    'blue': {
        'head' : (0.92, 0.78, 0.62),   # skin
        'torso': (0.15, 0.32, 0.88),   # blue armour
        'arm'  : (0.10, 0.24, 0.72),   # blue sleeve
        'leg'  : (0.26, 0.20, 0.48),   # dark trousers
    },
    'red': {
        'head' : (0.92, 0.78, 0.62),   # skin
        'torso': (0.88, 0.10, 0.10),   # red armour
        'arm'  : (0.72, 0.07, 0.07),   # red sleeve
        'leg'  : (0.46, 0.17, 0.17),   # dark trousers
    },
}


def _make_voxels(scheme):
    """
    Return a list of (ix, iy, iz, r, g, b) that define a 12-block humanoid.

    Layout (front view, y axis up, figure is 3 wide × 6 tall × 1 deep):

        y=5  . H .   ← head top
        y=4  . H .   ← head bottom
        y=3  A T A   ← upper torso  (A = arm, T = torso)
        y=2  A T A   ← lower torso
        y=1  L . R   ← upper legs
        y=0  L . R   ← lower legs

    ix ∈ {-1, 0, 1}  – centred on x=0 after the -0.5 mesh offset.
    """
    s = _SCHEMES[scheme]
    h, t, a, l = s['head'], s['torso'], s['arm'], s['leg']
    return [
        # Head (centre column)
        ( 0, 5, 0, *h),
        ( 0, 4, 0, *h),
        # Upper torso + arms
        (-1, 3, 0, *a),
        ( 0, 3, 0, *t),
        ( 1, 3, 0, *a),
        # Lower torso + arms
        (-1, 2, 0, *a),
        ( 0, 2, 0, *t),
        ( 1, 2, 0, *a),
        # Legs
        (-1, 1, 0, *l),
        ( 1, 1, 0, *l),
        (-1, 0, 0, *l),
        ( 1, 0, 0, *l),
    ]


# ---------------------------------------------------------------------------
# AI tuning constants (all time values in seconds)
# ---------------------------------------------------------------------------
VPLAYER_SPEED    = 5.0    # blocks / second while chasing
WANDER_SPEED     = 2.0    # blocks / second while wandering
ATTACK_RANGE     = 3.2    # blocks  – close-combat trigger distance
CHASE_RANGE      = 55.0   # blocks  – aggro range
MAX_HP           = 100
ATTACK_DAMAGE    = 12     # hp per strike
ATTACK_COOLDOWN  = 0.80   # s  between strikes
WANDER_INTERVAL  = 2.5    # s  between random direction changes
RESPAWN_TIME     = 4.0    # s  dead before respawn
DEATH_FALL_SPEED = 110.0  # degrees / second (tip-over animation)


class VoxelPlayer:
    """
    An AI-driven humanoid built entirely from coloured unit cubes.
    Two instances fight each other inside the voxel world.

    States
    ------
    wander  → random stroll; switches to chase when enemy enters range
    chase   → rush toward enemy
    attack  → melee strike on cooldown
    dead    → tips over; respawns after RESPAWN_TIME seconds
    """

    def __init__(self, app, position, scheme='blue', name='Fighter'):
        self.app    = app
        self.name   = name
        self.scheme = scheme

        self.position = glm.vec3(position)
        self.yaw      = random.uniform(0.0, 2.0 * math.pi)

        # Combat stats
        self.hp         = MAX_HP
        self.max_hp     = MAX_HP
        self.kill_count = 0

        # AI bookkeeping
        self.enemy         = None
        self.state         = 'wander'
        self.wander_timer  = random.uniform(0.5, WANDER_INTERVAL)
        self.wander_dir    = glm.vec3(math.cos(self.yaw), 0.0, math.sin(self.yaw))
        self.attack_timer  = 0.0
        self.respawn_timer = 0.0
        self.dead          = False
        self.dead_tilt     = 0.0   # degrees of tip-over (0 = upright, 90 = flat)

        # GPU mesh
        voxels     = _make_voxels(scheme)
        self.mesh  = VoxelBodyMesh(app, voxels)
        self.m_model = self._build_model_matrix()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_enemy(self, other: 'VoxelPlayer'):
        self.enemy = other

    def take_damage(self, amount: int):
        if self.dead:
            return
        self.hp = max(0, self.hp - amount)
        if self.hp == 0:
            self._die()

    def update(self, dt: float):
        """
        Advance AI logic by *dt* seconds.
        Call once per frame from Scene.update().
        """
        if self.dead:
            self._update_dead(dt)
        else:
            self._update_ai(dt)
            self.position.y = self._ground_y()

        self.m_model = self._build_model_matrix()

    def render(self):
        # flash briefly just before respawn
        if self.dead and self.respawn_timer < 0.5:
            if int(self.respawn_timer * 10) % 2 == 0:
                return
        self.mesh.program['m_model'].write(self.m_model)
        self.mesh.render()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _die(self):
        self.dead          = True
        self.state         = 'dead'
        self.respawn_timer = RESPAWN_TIME
        self.dead_tilt     = 0.0
        if self.enemy:
            self.enemy.kill_count += 1

    def _respawn(self):
        ox = random.uniform(-25.0, 25.0)
        oz = random.uniform(-25.0, 25.0)
        nx = float(glm.clamp(CENTER_XZ + ox, CHUNK_SIZE, (WORLD_W - 1) * CHUNK_SIZE))
        nz = float(glm.clamp(CENTER_XZ + oz, CHUNK_SIZE, (WORLD_D - 1) * CHUNK_SIZE))
        ny = float(get_height(int(nx), int(nz), self.app.terrain_type))
        self.position      = glm.vec3(nx, ny, nz)
        self.yaw           = random.uniform(0.0, 2.0 * math.pi)
        self.hp            = self.max_hp
        self.dead          = False
        self.dead_tilt     = 0.0
        self.attack_timer  = 0.0
        self.wander_timer  = random.uniform(0.5, WANDER_INTERVAL)
        self.state         = 'wander'

    def _ground_y(self) -> float:
        wx = int(glm.clamp(self.position.x, 1.0, WORLD_W * CHUNK_SIZE - 2.0))
        wz = int(glm.clamp(self.position.z, 1.0, WORLD_D * CHUNK_SIZE - 2.0))
        return float(get_height(wx, wz, self.app.terrain_type))

    def _build_model_matrix(self):
        m = glm.translate(glm.mat4(), self.position)
        m = glm.rotate(m, self.yaw, glm.vec3(0.0, 1.0, 0.0))
        if self.dead and self.dead_tilt > 0.0:
            # tip forward around the feet (translate up, rotate, translate back)
            m = glm.translate(m, glm.vec3(0.0, 0.0, 0.5))
            m = glm.rotate(m, glm.radians(self.dead_tilt), glm.vec3(1.0, 0.0, 0.0))
            m = glm.translate(m, glm.vec3(0.0, 0.0, -0.5))
        return m

    # ---------- state machine ----------

    def _update_dead(self, dt: float):
        self.dead_tilt     = min(self.dead_tilt + DEATH_FALL_SPEED * dt, 90.0)
        self.respawn_timer -= dt
        if self.respawn_timer <= 0.0:
            self._respawn()

    def _update_ai(self, dt: float):
        if not self.enemy or self.enemy.dead:
            self._wander(dt)
            return

        dist = math.sqrt(
            (self.position.x - self.enemy.position.x) ** 2 +
            (self.position.z - self.enemy.position.z) ** 2
        )

        if dist < ATTACK_RANGE:
            self.state = 'attack'
            self._attack(dt)
        elif dist < CHASE_RANGE:
            self.state = 'chase'
            self._chase(dt)
        else:
            self.state = 'wander'
            self._wander(dt)

    def _face_toward(self, target: glm.vec3):
        dx = target.x - self.position.x
        dz = target.z - self.position.z
        self.yaw = math.atan2(dx, dz)

    def _move_xz(self, dx: float, dz: float, speed: float, dt: float):
        length = math.sqrt(dx * dx + dz * dz)
        if length < 0.001:
            return
        nx = self.position.x + dx / length * speed * dt
        nz = self.position.z + dz / length * speed * dt
        self.position.x = float(glm.clamp(nx, CHUNK_SIZE, (WORLD_W - 1) * CHUNK_SIZE))
        self.position.z = float(glm.clamp(nz, CHUNK_SIZE, (WORLD_D - 1) * CHUNK_SIZE))

    def _chase(self, dt: float):
        dx = self.enemy.position.x - self.position.x
        dz = self.enemy.position.z - self.position.z
        self._face_toward(self.enemy.position)
        self._move_xz(dx, dz, VPLAYER_SPEED, dt)

    def _attack(self, dt: float):
        self._face_toward(self.enemy.position)
        self.attack_timer -= dt
        if self.attack_timer <= 0.0:
            self.enemy.take_damage(ATTACK_DAMAGE)
            self.attack_timer = ATTACK_COOLDOWN

    def _wander(self, dt: float):
        self.wander_timer -= dt
        if self.wander_timer <= 0.0:
            angle = random.uniform(0.0, 2.0 * math.pi)
            self.wander_dir   = glm.vec3(math.cos(angle), 0.0, math.sin(angle))
            self.wander_timer = random.uniform(1.2, WANDER_INTERVAL)
            self.yaw          = angle
        self._move_xz(self.wander_dir.x, self.wander_dir.z, WANDER_SPEED, dt)
