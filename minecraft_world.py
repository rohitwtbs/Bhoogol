"""
Minecraft World implementation for Bhoogol.
Extends the base World class to load chunks from Minecraft data.
"""

import numpy as np
import glm
from settings import *
from world_objects.chunk import Chunk
from voxel_handler import VoxelHandler
from tools.minecraft_world_viewer import MinecraftWorldLoader


class MinecraftWorldWrapper:
    """Wrapper that loads Minecraft world while maintaining compatibility with Bhoogol."""
    
    def __init__(self, app, minecraft_world_path):
        """Initialize Minecraft world wrapper."""
        self.app = app
        self.minecraft_loader = MinecraftWorldLoader(minecraft_world_path)
        self.chunks = [None for _ in range(WORLD_VOL)]
        self.voxels = np.empty([WORLD_VOL, CHUNK_VOL], dtype='uint8')
        
        # Get spawn position
        spawn = self.minecraft_loader.get_spawn_position()
        self.spawn_pos = spawn
        
        self.build_chunks()
        self.build_chunk_mesh()
        self.voxel_handler = VoxelHandler(self)
    
    def build_chunks(self):
        """Build chunk objects for Minecraft world."""
        world_info = self.minecraft_loader.get_world_info()
        spawn_x, spawn_y, spawn_z = self.spawn_pos
        
        print(f"Loading Minecraft world: {world_info['name']}")
        print(f"Spawn: {spawn_x}, {spawn_y}, {spawn_z}")
        
        # Calculate which Minecraft chunks to load around spawn
        spawn_chunk_x = spawn_x // 16
        spawn_chunk_z = spawn_z // 16
        
        loaded_chunks = 0
        non_empty_chunks = 0
        
        # Load chunks around spawn
        for bx in range(WORLD_W):
            for by in range(WORLD_H):
                for bz in range(WORLD_D):
                    chunk = Chunk(self, position=(bx, by, bz))
                    chunk_index = bx + WORLD_W * bz + WORLD_AREA * by
                    self.chunks[chunk_index] = chunk
                    
                    # Calculate which Minecraft chunk this corresponds to
                    # bx, bz are Bhoogol chunk positions, convert to Minecraft chunk coords
                    mc_chunk_x = spawn_chunk_x + (bx - WORLD_W // 2)
                    mc_chunk_z = spawn_chunk_z + (bz - WORLD_D // 2)
                    
                    # Load voxels from Minecraft
                    try:
                        voxel_data = self._load_minecraft_chunk(
                            mc_chunk_x, mc_chunk_z,
                            y_start=by * CHUNK_SIZE
                        )
                        self.voxels[chunk_index] = voxel_data
                        chunk.voxels = self.voxels[chunk_index]
                        
                        if np.any(voxel_data):
                            non_empty_chunks += 1
                            chunk.is_empty = False
                        
                        loaded_chunks += 1
                    except Exception as e:
                        print(f"Error loading chunk ({mc_chunk_x}, {mc_chunk_z}): {e}")
                        self.voxels[chunk_index] = np.zeros(CHUNK_VOL, dtype='uint8')
                        chunk.voxels = self.voxels[chunk_index]
        
        print(f"Loaded {loaded_chunks} chunks, {non_empty_chunks} non-empty")
    
    def _load_minecraft_chunk(self, chunk_x, chunk_z, y_start=0):
        """Load a Minecraft chunk and convert to voxel data."""
        voxels = np.zeros(CHUNK_VOL, dtype='uint8')
        
        try:
            # Load raw Minecraft chunk data
            nbt_chunk = self.minecraft_loader.region_set.get_chunk(chunk_x, chunk_z)
            if nbt_chunk is None:
                return voxels
            
            # Extract section data (keys are lowercase in newer Minecraft format)
            sections = {}
            try:
                if 'Level' in nbt_chunk:
                    level = nbt_chunk['Level']
                    if 'sections' in level:  # lowercase!
                        for section in level['sections']:
                            s_y = int(section['Y'].value)
                            if 'block_states' in section:  # lowercase!
                                block_states_obj = section['block_states']
                                if 'palette' in block_states_obj and 'data' in block_states_obj:
                                    sections[s_y] = {
                                        'palette': block_states_obj['palette'],
                                        'block_states': block_states_obj['data'],
                                    }
            except (KeyError, TypeError, AttributeError):
                return voxels
            
            if not sections:
                return voxels
            
            # Process each section
            for section_y, section_data in sections.items():
                # Calculate position in voxel array
                world_y = (section_y + 4) * 16  # Sections are 16 blocks tall
                local_y_start = world_y - y_start
                
                if local_y_start >= CHUNK_SIZE or local_y_start + 16 <= 0:
                    continue
                
                # Decode blocks from palette
                try:
                    palette = section_data['palette']
                    block_states = section_data['block_states']
                    
                    # Decode block data
                    block_array = self._decode_blocks(palette, block_states)
                    
                    # Copy to voxel array
                    for x in range(16):
                        for z in range(16):
                            for y in range(16):
                                local_y = local_y_start + y
                                if 0 <= local_y < CHUNK_SIZE:
                                    block_id = block_array[x, y, z]
                                    if block_id > 0:  # Skip air
                                        voxel_idx = x + z * CHUNK_SIZE + local_y * CHUNK_SIZE * CHUNK_SIZE
                                        if voxel_idx < CHUNK_VOL:
                                            voxels[voxel_idx] = block_id
                
                except Exception as e:
                    pass  # Silently skip problematic sections
        
        except Exception as e:
            pass  # Silently skip chunks with errors
        
        return voxels
    
    def _decode_blocks(self, palette, block_states):
        """Decode Minecraft block palette into block array."""
        blocks = np.zeros((16, 16, 16), dtype='uint8')
        
        if not palette or not block_states:
            return blocks
        
        try:
            # Determine bits per block
            palette_len = len(palette)
            if palette_len <= 1:
                bits_per_block = 1
            else:
                bits_per_block = max(4, (palette_len - 1).bit_length())
            
            # Create bit array from block states (long array [])
            bit_array = []
            for state_entry in block_states:
                # block_states is a TAG_Long_Array
                state_val = int(state_entry.value) if hasattr(state_entry, 'value') else int(state_entry)
                for i in range(64):
                    bit_array.append((state_val >> i) & 1)
            
            # Extract blocks
            block_index = 0
            for y in range(16):
                for z in range(16):
                    for x in range(16):
                        bit_pos = block_index * bits_per_block
                        block_bits = 0
                        
                        for i in range(bits_per_block):
                            if bit_pos + i < len(bit_array):
                                block_bits |= (bit_array[bit_pos + i] << i)
                        
                        # Look up in palette
                        if block_bits < len(palette):
                            palette_entry = palette[block_bits]
                            block_name = str(palette_entry['Name'].value) if hasattr(palette_entry['Name'], 'value') else str(palette_entry['Name'])
                            voxel_id = self._block_name_to_id(block_name)
                            blocks[x, y, z] = voxel_id
                        
                        block_index += 1
        
        except Exception as e:
            pass  # Silently handle issues
        
        return blocks
    
    def _block_name_to_id(self, block_name):
        """Convert Minecraft block name to voxel ID."""
        # Extract base name
        if ':' in block_name:
            block_name = block_name.split(':')[1]
        if '[' in block_name:
            block_name = block_name.split('[')[0]
        
        # Simple mapping
        block_map = {
            'air': 0,
            'stone': 1, 'granite': 1, 'diorite': 1, 'andesite': 1, 'deepslate': 1,
            'dirt': 2, 'coarse_dirt': 2, 'rooted_dirt': 2,
            'grass_block': 3,
            'oak_log': 4, 'spruce_log': 4, 'birch_log': 4, 'jungle_log': 4, 'acacia_log': 4, 'dark_oak_log': 4,
            'oak_leaves': 5, 'spruce_leaves': 5, 'birch_leaves': 5, 'jungle_leaves': 5, 'acacia_leaves': 5, 'dark_oak_leaves': 5,
            'sand': 6, 'red_sand': 6,
            'water': 7, 'seagrass': 7,
            'lava': 8,
            'snow_block': 9, 'snow': 9,
            'ice': 10, 'packed_ice': 10, 'blue_ice': 10,
            'oak_planks': 11,
        }
        
        return block_map.get(block_name, 1)  # Default to stone
    
    def build_chunk_mesh(self):
        """Build meshes for all chunks."""
        for chunk in self.chunks:
            if chunk is not None:
                chunk.build_mesh()
    
    def update(self):
        """Update world state."""
        self.voxel_handler.update()
    
    def render(self):
        """Render all chunks."""
        for chunk in self.chunks:
            if chunk is not None:
                chunk.render()

