"""
NBT (Named Binary Tag) reader for Minecraft world data.
Supports reading level.dat and region files.
"""

import os
from pathlib import Path
from nbt.nbt import NBTFile
from io import BytesIO


class NBTReader:
    """Reads and parses Minecraft NBT format files."""
    
    @staticmethod
    def read_level_dat(world_path):
        """
        Read level.dat from a Minecraft world folder.
        Returns world metadata including world name, seed, etc.
        """
        level_dat_path = os.path.join(world_path, "level.dat")
        
        if not os.path.exists(level_dat_path):
            raise FileNotFoundError(f"level.dat not found at {level_dat_path}")
        
        try:
            nbt_file = NBTFile(filename=level_dat_path)
            world_info = {
                'name': str(nbt_file['Data']['LevelName'].value) if 'LevelName' in nbt_file['Data'] else 'Minecraft World',
                'seed': int(nbt_file['Data']['WorldGenSettings']['seed'].value) if 'WorldGenSettings' in nbt_file['Data'] else 0,
                'spawn_x': int(nbt_file['Data']['SpawnX'].value) if 'SpawnX' in nbt_file['Data'] else 0,
                'spawn_y': int(nbt_file['Data']['SpawnY'].value) if 'SpawnY' in nbt_file['Data'] else 64,
                'spawn_z': int(nbt_file['Data']['SpawnZ'].value) if 'SpawnZ' in nbt_file['Data'] else 0,
            }
            return world_info
        except Exception as e:
            print(f"Error reading level.dat: {e}")
            # Return defaults if parsing fails
            return {
                'name': 'Minecraft World',
                'seed': 0,
                'spawn_x': 0,
                'spawn_y': 64,
                'spawn_z': 0,
            }
    
    @staticmethod
    def read_chunk_data(nbt_chunk):
        """
        Extract block data from a chunk NBT tag.
        Returns section data for the chunk.
        """
        sections = {}
        
        try:
            if 'Level' in nbt_chunk and 'Sections' in nbt_chunk['Level']:
                for section in nbt_chunk['Level']['Sections']:
                    y = int(section['Y'].value)
                    if 'BlockStates' in section and 'Palette' in section:
                        sections[y] = {
                            'palette': section['Palette'],
                            'block_states': section['BlockStates'],
                        }
        except KeyError:
            pass
        
        return sections
    
    @staticmethod
    def get_block_id_from_palette(block_index, palette, block_states):
        """
        Decode block ID from palette and block states.
        Uses bit manipulation to extract block data.
        """
        if block_index >= len(palette):
            return 0
        
        try:
            block_name = str(palette[block_index]['Name'])
            return NBTReader.block_name_to_id(block_name)
        except (KeyError, IndexError):
            return 0
    
    @staticmethod
    def block_name_to_id(block_name):
        """
        Convert Minecraft block name to simplified voxel ID.
        Maps Minecraft blocks to 0-255 range.
        """
        # Block ID mapping (simplified - maps to voxel types)
        block_map = {
            'air': 0,
            'stone': 1,
            'granite': 1,
            'diorite': 1,
            'andesite': 1,
            'dirt': 2,
            'coarse_dirt': 2,
            'grass_block': 3,
            'grass': 0,
            'oak_log': 4,
            'spruce_log': 4,
            'birch_log': 4,
            'jungle_log': 4,
            'acacia_log': 4,
            'dark_oak_log': 4,
            'oak_leaves': 5,
            'spruce_leaves': 5,
            'birch_leaves': 5,
            'jungle_leaves': 5,
            'acacia_leaves': 5,
            'dark_oak_leaves': 5,
            'sand': 6,
            'red_sand': 6,
            'water': 7,
            'lava': 8,
            'snow_block': 9,
            'ice': 10,
        }
        
        # Extract base name from namespaced ID
        if ':' in block_name:
            block_name = block_name.split(':')[1]
        
        # Strip properties (e.g., "oak_log[axis=y]" -> "oak_log")
        if '[' in block_name:
            block_name = block_name.split('[')[0]
        
        return block_map.get(block_name, 1)  # Default to stone if unknown
