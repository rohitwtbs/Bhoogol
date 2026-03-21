# Minecraft World Viewer

An independent Minecraft world viewer built with the Bhoogol voxel engine. Load and explore your Minecraft worlds in real-time with full rendering support.

## Features

- ✅ Load Minecraft world folders (level.dat + region files)
- ✅ Real-time 3D rendering with Bhoogol's voxel engine
- ✅ Smooth camera controls with mouse look
- ✅ Block placement and removal
- ✅ Automatic spawn position detection
- ✅ Support for Minecraft 1.13+ worlds (Anvil format)

## Prerequisites

- Python 3.8+
- Minecraft world folder containing `level.dat` and `region/` directory

## Installation

1. Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

2. Verify the `nbt` library is installed:
```bash
pip install nbt==1.5.1
```

## Usage

### Basic Usage

```bash
python minecraft_viewer.py /path/to/minecraft/world
```

### Examples

**On Linux/Mac:**
```bash
python minecraft_viewer.py ~/.minecraft/saves/My_World
```

**On Windows:**
```bash
python minecraft_viewer.py "C:\Users\YourName\AppData\Roaming\.minecraft\saves\My_World"
```

## Controls

| Key | Action |
|-----|--------|
| **W** | Move forward |
| **A** | Move left |
| **S** | Move backward |
| **D** | Move right |
| **Q** | Move down |
| **E** | Move up |
| **Mouse** | Look around |
| **R** | Remove block |
| **E** | Place block |
| **ESC** | Exit |

## How It Works

The viewer consists of several components:

### 1. **NBT Reader** (`nbt_reader.py`)
- Reads Minecraft's Named Binary Tag (NBT) format
- Parses `level.dat` for world metadata (name, seed, spawn point)
- Extracts chunk data and block palettes

### 2. **Region Parser** (`region_parser.py`)
- Parses Minecraft region files (`.mca` format, Anvil)
- Handles chunk decompression (zlib/gzip)
- Manages multiple region files

### 3. **Minecraft Loader** (`minecraft_loader.py`)
- Loads chunks from Minecraft world data
- Converts Minecraft block IDs to Bhoogol voxel IDs
- Handles block palette decoding
- Caches chunks for performance

### 4. **Viewer** (`minecraft_viewer.py`)
- Main application entry point
- Integrates with Bhoogol's rendering engine
- Provides player movement and camera control
- Handles block editing

## Block Mapping

Minecraft blocks are mapped to simplified voxel types:

| Minecraft Block | Voxel ID | Color |
|-----------------|----------|-------|
| Air | 0 | Transparent |
| Stone | 1 | Gray |
| Dirt | 2 | Brown |
| Grass Block | 3 | Green |
| Logs | 4 | Brown |
| Leaves | 5 | Dark Green |
| Sand | 6 | Yellow |
| Water | 7 | Blue |
| Lava | 8 | Red |
| Ice | 10 | Light Blue |

You can extend the `BLOCK_ID_MAP` in `minecraft_loader.py` to support more blocks.

## Troubleshooting

### "level.dat not found"
Make sure you're pointing to the actual Minecraft world folder, not the `.minecraft` folder. The world folder contains:
```
world_folder/
├── level.dat
├── region/
│   ├── r.0.0.mca
│   ├── r.0.1.mca
│   └── ...
└── ...
```

### Low Performance
- Reduce `WORLD_W` and `WORLD_D` in `settings.py`
- Reduce view distance by decreasing `FAR` distance
- Request smaller chunk loads

### Blocks Not Rendering
- Check that your world blocks are in the `BLOCK_ID_MAP`
- Verify the region files are not corrupted
- Try updating to the latest Minecraft version format

## Extending the Viewer

### Add New Blocks

Edit `minecraft_loader.py` and add to `BLOCK_ID_MAP`:

```python
BLOCK_ID_MAP = {
    'your_block_name': 100,  # Your custom voxel ID
    # ... other blocks
}
```

### Change Rendering

Modify settings in `settings.py`:
- `WORLD_W`, `WORLD_H`, `WORLD_D`: World size
- `CHUNK_SIZE`: Voxel chunk size
- `FAR`: Render distance

### Custom World Loading

Subclass `MinecraftWorldWrapper` to customize chunk loading behavior.

## Performance Notes

- Large worlds may take time to load initially
- Chunk caching improves performance for revisited areas
- Consider using smaller world sections for better performance
- Render distance can be adjusted via the `FAR` setting

## Limitations

- Only supports Anvil format (.mca) region files
- Some blocks may not have accurate voxel representations
- Biome-specific rendering is simplified
- Textures are procedural, not from Minecraft texture pack

## Future Improvements

- [ ] Support for more block types with proper rendering
- [ ] Schematic file support
- [ ] World editing and saving
- [ ] Texture pack integration
- [ ] Performance optimization for larger worlds
- [ ] Multiplayer support

## License

This viewer integrates with Bhoogol. Check LICENSE files for details.

## Troubleshooting

If you encounter issues:

1. Check that Python 3.8+ is installed
2. Verify all dependencies: `pip install -r requirements.txt`
3. Ensure your Minecraft world is not corrupted
4. Check console output for detailed error messages

For issues with Minecraft world format, see:
- [Minecraft Wiki - NBT Format](https://minecraft.wiki/w/NBT_format)
- [Minecraft Wiki - Region Format](https://minecraft.wiki/w/Region_file_format)
