import numpy as np

class MeshGenerator3D:
    """Generates 3D soft-body volumetric meshes and spring mass structures for assemblies."""
    
    @staticmethod
    def create_block_3d(dimensions=(3, 3, 3), spacing=0.5, origin=(0, 0, 0), material_id="default"):
        """Creates a 3D structural voxel block of interconnected mass points and springs."""
        nx, ny, nz = dimensions
        ox, oy, oz = origin
        
        nodes = []
        node_map = {}
        idx = 0
        
        # 1. Generate 3D Grid Nodes
        for x in range(nx):
            for y in range(ny):
                for z in range(nz):
                    pos = np.array([
                        ox + x * spacing,
                        oy + y * spacing,
                        oz + z * spacing
                    ], dtype=np.float32)
                    nodes.append(pos)
                    node_map[(x, y, z)] = idx
                    idx += 1
                    
        springs = []
        seen_springs = set()

        def add_spring(i, j, spring_type="structural"):
            pair = tuple(sorted((i, j)))
            if pair not in seen_springs:
                seen_springs.add(pair)
                p1, p2 = nodes[i], nodes[j]
                rest_length = np.linalg.norm(p1 - p2)
                springs.append({
                    'node1': i,
                    'node2': j,
                    'rest_length': rest_length,
                    'type': spring_type
                })

        # 2. Generate 3D Structural, Shear, and Diagonal Springs
        for (x, y, z), i in node_map.items():
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    for dz in [-1, 0, 1]:
                        if dx == 0 and dy == 0 and dz == 0:
                            continue
                        neighbor = (x + dx, y + dy, z + dz)
                        if neighbor in node_map:
                            j = node_map[neighbor]
                            dist_sum = abs(dx) + abs(dy) + abs(dz)
                            stype = "structural" if dist_sum == 1 else "shear"
                            add_spring(i, j, stype)

        return {
            'nodes': np.array(nodes, dtype=np.float32),
            'springs': springs,
            'material': material_id,
            'grid_dims': dimensions
        }

