# Configuration Examples

This file shows how to customize the Minecraft World Viewer for different use cases.

## Example 1: Small Worlds / Testing

Edit `settings.py` to load smaller regions:

```python
# Smaller world for testing/performance
WORLD_W, WORLD_H = 10, 2  # Reduced from 20, 2
WORLD_D = WORLD_W

# Closer render distance
FAR = 500.0  # Reduced from 2000.0

# Faster chunk processing
MAX_RAY_DIST = 4  # Reduced from 6
```

Run:
```bash
python minecraft_viewer.py ~/.minecraft/saves/My_Small_World
```

## Example 2: Large Worlds / Exploration

Edit `settings.py` for maximum render distance:

```python
# Larger render distance for exploration
FAR = 3000.0  # Increased from 2000.0

# Larger world view
WORLD_W, WORLD_H = 30, 3

# More aggressive chunk loading
# (hardware dependent)
```

Tips:
- Use on high-end hardware
- May see slower initial load times
- Great for panorama screenshots

## Example 3: Custom Block Rendering

Edit `minecraft_loader.py`:

```python
BLOCK_ID_MAP = {
    'air': 0,
    'stone': 1,
    'granite': 1,
    'dirt': 2,
    'grass_block': 3,
    'oak_log': 4,
    'spruce_log': 4,
    
    # Add custom blocks
    'diamond_ore': 20,
    'deepslate_diamond_ore': 20,
    'gold_ore': 21,
    'iron_ore': 22,
    'coal_ore': 23,
    'redstone_ore': 24,
    'lapis_ore': 25,
    'obsidian': 26,
    'crying_obsidian': 26,
    'netherrack': 27,
    'soul_sand': 28,
    'nether_wart_block': 29,
    'warped_wart_block': 29,
    'blackstone': 30,
}
```

This allows better differentiation of ore blocks and nether materials.

## Example 4: Cinematic Camera Settings

Edit `settings.py` for smooth camera movement:

```python
# Slower rotation for smooth camera movements
PLAYER_ROT_SPEED = 0.001  # Reduced from 0.003

# Slower forward speed for controlled exploration
PLAYER_SPEED = 0.008  # Reduced from 0.012

# Increased FOV for cinematic feel
FOV_DEG = 70  # Increased from 50
```

Use case: Creating video content, cinematic exploration.

## Example 5: High Performance / Mobile

Edit `settings.py` for maximum FPS:

```python
import inspect

# Minimal geometry
CHUNK_SIZE = 32  # Reduced from 48

# Aggressive culling
WORLD_W, WORLD_H = 5, 1
WORLD_D = 5

# Close render distance
FAR = 200.0

# Lower target FPS
# (In minecraft_viewer.py, change: self.clock.tick(30))
```

Edit `minecraft_viewer.py`:
```python
# In the run() method, change to:
self.clock.tick(30)  # Lower FPS target
```

## Example 6: Survival World with Cave Systems

Create a custom settings file `settings_caves.py`:

```python
# Settings optimized for cave exploration

CHUNK_SIZE = 48
WORLD_W, WORLD_H, WORLD_D = 20, 5, 20  # Taller world for caves

FAR = 1500.0  # Medium render distance

# Faster movement for cave navigation
PLAYER_SPEED = 0.015

# More sensitive camera for precision
PLAYER_ROT_SPEED = 0.004
```

Run with:
```bash
PYTHONPATH=. python -c "
import sys
sys.path.insert(0, '.')
from settings_caves import *
from minecraft_viewer import MinecraftViewer
import sys
viewer = MinecraftViewer(sys.argv[1])
viewer.run()
" ~/.minecraft/saves/My_Survival_World
```

## Example 7: Multiplayer Viewer (Future)

Planned configuration for viewing multiple players:

```python
# (Not yet implemented, showing future structure)

class MultiplayerViewerSettings:
    """Settings for future multiplayer viewer."""
    
    ENABLE_PLAYER_TRACKING = True
    TRACK_PLAYERS = ['Player1', 'Player2']
    
    # Show other player positions
    SHOW_PLAYER_MARKERS = True
    PLAYER_MARKER_HEIGHT = 10
    
    # Name tags
    SHOW_NAME_TAGS = True
```

## Example 8: Custom World Renderer

Create `custom_renderer.py` to extend the viewer:

```python
from minecraft_viewer import MinecraftViewer
from settings import *
import glm

class CustomWorldRenderer(MinecraftViewer):
    """Custom renderer with additional features."""
    
    def __init__(self, minecraft_world_path):
        super().__init__(minecraft_world_path)
        self.draw_bounds = True
        self.draw_spawn_point = True
    
    def render(self):
        """Override render to add custom elements."""
        self.ctx.clear(color=(0.1, 0.16, 0.8))
        self.world.render()
        
        # Add custom rendering here
        if self.draw_spawn_point:
            self._draw_spawn_marker()
        
        pg.display.flip()
    
    def _draw_spawn_marker(self):
        """Draw a marker at spawn point."""
        # Implementation would go here
        pass

if __name__ == '__main__':
    import sys
    viewer = CustomWorldRenderer(sys.argv[1])
    viewer.run()
```

## Performance Tuning Reference

| Setting | Impact | Value Range |
|---------|--------|-------------|
| `WORLD_W` / `WORLD_D` | Memory & Render Time | 5-50 |
| `WORLD_H` | Vertical view | 1-5 |
| `FAR` | Render Distance | 100-5000 |
| `CHUNK_SIZE` | Chunk resolution | 16-64 |
| `PLAYER_SPEED` | Movement speed | 0.001-0.05 |
| `PLAYER_ROT_SPEED` | Camera sensitivity | 0.001-0.01 |

## Command Line Variants

### Batch Processing Script

Create `batch_load.sh`:

```bash
#!/bin/bash
# Load multiple worlds in sequence

WORLDS=(
    ~/.minecraft/saves/World1
    ~/.minecraft/saves/World2
    ~/.minecraft/saves/World3
)

for world in "${WORLDS[@]}"; do
    echo "Loading $world..."
    python minecraft_viewer.py "$world"
done
```

### World Comparison

Create `compare_worlds.sh`:

```bash
#!/bin/bash
# Open two terminals to compare worlds side-by-side

world1=$1
world2=$2

echo "Opening worlds..."
python minecraft_viewer.py "$world1" &
sleep 2
python minecraft_viewer.py "$world2" &

wait
```

Usage:
```bash
chmod +x compare_worlds.sh
./compare_worlds.sh ~/.minecraft/saves/World1 ~/.minecraft/saves/World2
```

## Testing Checklist

Use these configurations to test different scenarios:

- [ ] Small test world (< 100 chunks)
- [ ] Large survival world (> 10,000 chunks)
- [ ] Nether world (custom block mapping)
- [ ] Flat world (simple terrain)
- [ ] Amplified world (huge terrain variation)
- [ ] Ocean world (lots of water)
- [ ] Mushroom world (edge case)

## Quick Presets

Add these to a config file for easy switching:

```python
PRESETS = {
    'test': {
        'WORLD_W': 10,
        'WORLD_H': 2,
        'FAR': 500,
    },
    'explore': {
        'WORLD_W': 30,
        'WORLD_H': 3,
        'FAR': 3000,
        'PLAYER_SPEED': 0.015,
    },
    'cinematic': {
        'PLAYER_ROT_SPEED': 0.001,
        'PLAYER_SPEED': 0.005,
        'FOV_DEG': 70,
    },
    'performance': {
        'CHUNK_SIZE': 32,
        'WORLD_W': 5,
        'FAR': 200,
    }
}
```

Choose at runtime:
```python
selected_preset = 'explore'
for key, value in PRESETS[selected_preset].items():
    globals()[key] = value
```

## Notes

- Always test settings on your specific hardware
- Start conservative, then increase settings
- Monitor FPS and memory usage
- Cache renders when possible
- Use profiling tools to identify bottlenecks
