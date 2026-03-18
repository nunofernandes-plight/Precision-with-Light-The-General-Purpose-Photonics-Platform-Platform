import numpy as np
import trimesh
from ..1_intent_layer.schemas import PCFGeometry

class NanoscribeExporter:
    """
    The 'Loading Dock': Converts AI-generated 2D parameters into 3D printable STL files.
    """
    def __init__(self, extrusion_length_um: float = 500.0):
        self.z_length = extrusion_length_um

    def create_pcf_mesh(self, geometry: PCFGeometry, filename: str = "pcf_export.stl"):
        """
        Generates a 3D cylinder (cladding) and subtracts a hexagonal lattice of holes.
        """
        pitch = geometry.pitch_um
        hole_radius = (geometry.d_over_pitch * pitch) / 2
        cladding_radius = pitch * (geometry.rings + 1)

        print(f"[Exporter] Building 3D Mesh: {geometry.rings} rings, {pitch}um pitch...")

        # 1. Create the bulk Cladding Cylinder
        main_cladding = trimesh.creation.cylinder(radius=cladding_radius, height=self.z_length)

        # 2. Generate the Hole Pattern for subtraction
        hole_meshes = []
        for r in range(1, geometry.rings + 1):
            for i in range(6 * r):
                angle = i * (2 * np.pi / (6 * r))
                x = r * pitch * np.cos(angle)
                y = r * pitch * np.sin(angle)
                
                # Create hole cylinder (slightly taller to ensure clean boolean subtraction)
                hole = trimesh.creation.cylinder(radius=hole_radius, height=self.z_length + 10)
                hole.apply_translation([x, y, 0])
                hole_meshes.append(hole)

        # 3. Perform Boolean Subtraction (Cladding - Holes)
        # In a high-speed API, you might use 'manifold' or 'blender' for faster booleans
        final_fiber = main_cladding
        for h in hole_meshes:
            final_fiber = final_fiber.difference(h)

        # 4. Export for Nanoscribe
        final_fiber.export(filename)
        print(f"✅ Export Success: {filename} is ready for 3D Printing.")
        return filename
