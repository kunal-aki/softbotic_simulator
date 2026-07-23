import numpy as np

class SoftBody3D:
    """Represents a 3D inflatable/actuated soft robotic object in space."""
    def __init__(self, obj_id, mesh_data, material_props=None):
        self.id = obj_id
        self.positions = np.copy(mesh_data['nodes'])
        self.velocities = np.zeros_like(self.positions)
        self.forces = np.zeros_like(self.positions)
        self.masses = np.ones(len(self.positions), dtype=np.float32) * 0.1
        self.springs = mesh_data['springs']
        self.material = material_props or {'stiffness': 300.0, 'damping': 2.5}
        self.actuation_phase = 0.0
        self.is_actuated = False
        self.color = (0.2, 0.6, 0.9, 0.8) # Default aesthetic soft-robotic blue

    def snap_to_3d_grid(self, grid_size=0.5):
        """Snaps object origin and nodes to the nearest 3D assembly grid point."""
        center = np.mean(self.positions, axis=0)
        snapped_center = np.round(center / grid_size) * grid_size
        offset = snapped_center - center
        self.positions += offset

    def update_actuation(self, dt, pressure_factor=1.0):
        """Inflates/contracts 3D actuators along active spring pathways."""
        if not self.is_actuated:
            return
        
        self.actuation_phase += dt * 3.0
        expansion = 1.0 + 0.25 * np.sin(self.actuation_phase) * pressure_factor
        
        for spring in self.springs:
            if spring['type'] == "structural":
                spring['current_rest_length'] = spring['rest_length'] * expansion
            else:
                spring['current_rest_length'] = spring['rest_length']


