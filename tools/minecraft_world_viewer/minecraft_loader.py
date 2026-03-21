"""
Minecraft world loader for Bhoogol voxel engine.
Converts Minecraft world data to Bhoogol chunk format.
"""

import numpy as np
from tools.minecraft_world_viewer.nbt_reader import NBTReader
from tools.minecraft_world_viewer.region_parser import RegionSet
import os


class MinecraftWorldLoader:
    """Loads and converts Minecraft worlds for rendering in Bhoogol."""
    
    # Block mappings for Minecraft -> Bhoogol voxel IDs
    BLOCK_ID_MAP = {
        'air': 0,
        'stone': 1,
        'granite': 1,
        'diorite': 1,
        'andesite': 1,
        'deepslate': 1,
        'dirt': 2,
        'grass_block': 3,
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
        'water': 7,
        'lava': 8,
        'snow_block': 9,
        'ice': 10,
        'oak_planks': 11,
        'spruce_planks': 11,
        'birch_planks': 11,
    }
    
    def __init__(self, world_path):
        """Initialize Minecraft world loader."""
        self.world_path = world_path
        self.region_set = RegionSet(world_path)
        self.world_info = NBTReader.read_level_dat(world_path)
        self.chunk_cache = {}  # Cache for loaded chunks
    
    def get_world_info(self):
        """Get world metadata."""
        return self.world_info
    
    def load_chunk(self, chunk_x, chunk_z, chunk_size=48, y_offset=0):
        """
        Load a Minecraft chunk and convert to Bhoogol format.
        
        Args:
            chunk_x, chunk_z: Chunk coordinates
            chunk_size: Size of output voxel chunk
            y_offset: Starting Y position in the output voxel array
        
        Returns:
            numpy array of voxels (chunk_size * chunk_size * chunk_size)
        """
        cache_key = (chunk_x, chunk_z, y_offset)
        if cache_key in self.chunk_cache:
            return self.chunk_cache[cache_key]
        
        voxels = np.zeros((chunk_size, chunk_size, chunk_size), dtype='uint8')
        
        try:
            nbt_chunk = self.region_set.get_chunk(chunk_x, chunk_z)
            if nbt_chunk is None:
                return voxels
            
            sections = NBTReader.read_chunk_data(nbt_chunk)
            
            # Process each section (Y levels)
            for section_y, section_data in sections.items():
                if section_y < 0 or section_y >= 24:  # MC 1.18+: sections -64 to 319
                    continue
                
                # Convert section Y to world Y
                world_y_start = (section_y + 4) * 16  # Sections are 16 blocks tall
                
                try:
                    palette = section_data['palette']
                    block_states = section_data.get('block_states', [])
                    
                    # Decode blocks from the section
                    block_data = self._decode_section_blocks(
                        palette, block_states, chunk_size, world_y_start, y_offset
                    )
                    
                    if block_data is not None:
                        # Add blocks to voxel array
                        for x in range(16):
                            for z in range(16):
                                for y in range(16):
                                    local_y = world_y_start + y - y_offset
                                    if 0 <= local_y < chunk_size:
                                        block_id = block_data[x, y, z]
                                        chunk_x_local = chunk_x % chunk_size
                                        voxels[chunk_x_local, local_y, z] = block_id
                except Exception as e:
                    print(f"Error decoding section {section_y}: {e}")
                    continue
        
        except Exception as e:
            print(f"Error loading chunk ({chunk_x}, {chunk_z}): {e}")
        
        self.chunk_cache[cache_key] = voxels
        return voxels
    
    def _decode_section_blocks(self, palette, block_states, chunk_size, world_y, y_offset):
        """
        Decode Minecraft block palette into block data.
        
        Returns:
            16x16x16 array of block IDs
        """
        blocks = np.zeros((16, 16, 16), dtype='uint8')
        
        if not palette or not block_states:
            return blocks
        
        try:
            # Determine bits per block
            palette_len = len(palette)
            bits_per_block = max(4, (palette_len - 1).bit_length())
            if bits_per_block > 8:
                bits_per_block = 15  # For 1.18+
            
            # Convert block states to bits
            bit_array = []
            for state in block_states:
                state_int = int(state)
                for i in range(64):  # 64 bits per long
                    bit_array.append((state_int >> i) & 1)
            
            # Extract block indices from bit array
            block_index = 0
            for y in range(16):
                for z in range(16):
                    for x in range(16):
                        bit_pos = block_index * bits_per_block
                        block_bits = 0
                        
                        for i in range(bits_per_block):
                            if bit_pos + i < len(bit_array):
                                block_bits |= (bit_array[bit_pos + i] << i)
                        
                        # Look up block ID from palette
                        if block_bits < len(palette):
                            block_name = str(palette[block_bits]['Name'])
                            voxel_id = self._block_name_to_id(block_name)
                            blocks[x, y, z] = voxel_id
                        
                        block_index += 1
        
        except Exception as e:
            print(f"Error decoding blocks: {e}")
        
        return blocks
    
    def _block_name_to_id(self, block_name):
        """Convert Minecraft block name to Bhoogol voxel ID."""
        # Extract base name from namespaced ID
        if ':' in block_name:
            block_name = block_name.split(':')[1]
        
        # Strip properties
        if '[' in block_name:
            block_name = block_name.split('[')[0]
        
        return self.BLOCK_ID_MAP.get(block_name, 1)  # Default to stone
    
    def get_spawn_position(self):
        """Get world spawn position."""
        info = self.world_info
        return (info['spawn_x'], info['spawn_y'], info['spawn_z'])
