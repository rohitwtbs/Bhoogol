# Quick Start Guide - Minecraft World Viewer

## 1. Prepare Your World

Make sure you have a valid Minecraft world folder. The minimum required files:
```
my_world/
├── level.dat          (World metadata)
└── region/
    └── r.0.0.mca     (At least one region file)
```

## 2. Find Your World

**Windows:**
- Open File Explorer
- Navigate to: `%APPDATA%\.minecraft\saves\`
- Copy your world folder path

**Mac:**
- Open Finder
- Press `Cmd + Shift + G` 
- Go to: `~/Library/Application Support/minecraft/saves/`

**Linux:**
- `~/.minecraft/saves/` or `~/.var/app/com.mojang.mcjavalinux/.minecraft/saves/`

## 3. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Ensure NBT library is installed
pip install nbt==1.5.1
```

## 4. Run the Viewer

```bash
# Basic usage
python minecraft_viewer.py /path/to/your/world

# Example on Linux/Mac
python minecraft_viewer.py ~/.minecraft/saves/My_Survival_World

# Example on Windows (use backslashes or quotes)
python minecraft_viewer.py "C:\Users\YourName\AppData\Roaming\.minecraft\saves\My_World"
```

## 5. Verify It Works

You should see:
1. A game window open with the Minecraft world
2. Console output showing world loading progress
3. Your player spawning at the world's spawn point

## Keyboard Controls

```
WASD  - Movement (forward, left, back, right)
Q/E   - Down/Up movement
Mouse - Look around
R     - Remove block
E     - Place block
ESC   - Exit
```

## Common Issues

### "level.dat not found"
```
❌ Wrong: C:\Users\...\AppData\Roaming\.minecraft\saves\
✅ Correct: C:\Users\...\AppData\Roaming\.minecraft\saves\MyWorld\
```

### Large Worlds Load Slowly
- This is normal for large worlds
- Initial chunk loading can take 1-2 minutes
- Subsequent loads are faster due to caching

### Low FPS
- Close other applications
- Reduce render distance in `settings.py`
- Use a smaller world section

### Blocks Look Wrong
- Some blocks may not have perfect voxel representations
- This is expected - see block mapping in README.md
- You can customize block mapping in `minecraft_loader.py`

## Next Steps

- Edit `settings.py` to customize viewing options
- Explore `minecraft_loader.py` to add more block types
- Check console output for debugging information

## Getting Help

Check the main README.md for:
- Full feature list
- Block mapping details
- Extending the viewer
- Performance optimization tips
