"""
Minecraft region file (.mca) parser.
Handles reading chunk data from region files in Anvil format.
"""

import struct
import zlib
import gzip
import os
from io import BytesIO
from nbt.nbt import NBTFile


class RegionFile:
    """Parses Minecraft region files (Anvil format)."""
    
    SECTOR_SIZE = 4096  # Each sector is 4KB
    
    def __init__(self, region_path):
        """Initialize region file parser."""
        self.region_path = region_path
        self.file_data = None
        self._load_file()
    
    def _load_file(self):
        """Load region file into memory."""
        if not os.path.exists(self.region_path):
            raise FileNotFoundError(f"Region file not found: {self.region_path}")
        
        with open(self.region_path, 'rb') as f:
            self.file_data = f.read()
    
    def get_chunk(self, local_x, local_z):
        """
        Extract chunk data from region file.
        local_x, local_z: position within region (0-31)
        Returns NBT chunk data or None if not present.
        """
        if local_x < 0 or local_x >= 32 or local_z < 0 or local_z >= 32:
            return None
        
        # Chunk offset is stored in first 4KB of region file
        offset_index = (local_x + local_z * 32) * 4
        
        if offset_index + 4 > len(self.file_data):
            return None
        
        # Read 3-byte offset + 1-byte sector count
        offset_data = self.file_data[offset_index:offset_index + 4]
        offset_sectors = struct.unpack('>I', b'\x00' + offset_data[:3])[0]
        sector_count = offset_data[3]
        
        if offset_sectors == 0 or sector_count == 0:
            return None  # Chunk doesn't exist
        
        # Read timestamp (not essential for loading)
        timestamp_index = 4096 + offset_index
        
        # Seek to chunk data
        chunk_offset = offset_sectors * self.SECTOR_SIZE
        
        if chunk_offset >= len(self.file_data):
            return None
        
        try:
            # Read chunk data length (first 4 bytes of chunk data)
            chunk_length = struct.unpack('>I', self.file_data[chunk_offset:chunk_offset + 4])[0]
            compression_type = self.file_data[chunk_offset + 4]
            
            # Read compressed data
            compressed_data = self.file_data[chunk_offset + 5:chunk_offset + 5 + chunk_length - 1]
            
            if compression_type == 2:  # Zlib compression
                decompressed_data = zlib.decompress(compressed_data)
                # NBTFile expects gzip, so wrap decompressed data
                gzip_stream = BytesIO()
                with gzip.GzipFile(fileobj=gzip_stream, mode='wb') as gz:
                    gz.write(decompressed_data)
                gzip_stream.seek(0)
            elif compression_type == 1:  # Gzip compression (already gzipped)
                gzip_stream = BytesIO(compressed_data)
            else:
                return None
            
            # Parse NBT data
            nbt_data = NBTFile(fileobj=gzip_stream)
            return nbt_data
        except Exception as e:
            print(f"Error reading chunk at ({local_x}, {local_z}): {e}")
            return None
    
    @staticmethod
    def get_region_coords(world_x, world_z):
        """Convert world coordinates to region coordinates."""
        region_x = world_x // 32
        region_z = world_z // 32
        return region_x, region_z
    
    @staticmethod
    def get_local_chunk_coords(world_x, world_z):
        """Get local chunk position within region (0-31)."""
        local_x = (world_x // 16) % 32
        local_z = (world_z // 16) % 32
        return local_x, local_z


class RegionSet:
    """Manages multiple region files for a Minecraft world."""
    
    def __init__(self, world_path):
        """Initialize region set for a world."""
        self.world_path = world_path
        self.region_dir = os.path.join(world_path, "region")
        self.regions = {}  # Cache for loaded regions
    
    def get_chunk(self, chunk_x, chunk_z):
        """
        Get chunk from region files.
        chunk_x, chunk_z: chunk coordinates (not world coordinates)
        """
        if not os.path.exists(self.region_dir):
            return None
        
        # Calculate region coordinates
        region_x = chunk_x // 32
        region_z = chunk_z // 32
        
        # Calculate local position within region
        local_x = chunk_x % 32
        local_z = chunk_z % 32
        
        region_key = (region_x, region_z)
        
        # Load region if not cached
        if region_key not in self.regions:
            region_path = os.path.join(
                self.region_dir,
                f"r.{region_x}.{region_z}.mca"
            )
            
            if not os.path.exists(region_path):
                return None
            
            try:
                self.regions[region_key] = RegionFile(region_path)
            except Exception as e:
                print(f"Error loading region r.{region_x}.{region_z}: {e}")
                return None
        
        region = self.regions[region_key]
        return region.get_chunk(local_x, local_z)
