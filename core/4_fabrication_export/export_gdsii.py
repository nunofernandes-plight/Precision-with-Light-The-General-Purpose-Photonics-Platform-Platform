import gdstk
from ..1_intent_layer.schemas import PCFGeometry

class GDSIIExporter:
    """
    The 'Foundry Interface': Converts geometries into GDSII binary format.
    Standard for Silicon Photonics and mask-making.
    """
    def __init__(self, lib_name: str = "PLIGHT_LIB"):
        self.lib = gdstk.Library(lib_name)
        self.cell = self.lib.new_cell("PCF_CROSS_SECTION")

    def generate_layout(self, geometry: PCFGeometry, output_path: str = "pcf_mask.gds"):
        pitch = geometry.pitch_um
        radius = (geometry.d_over_pitch * pitch) / 2
        
        # Layer 1: Cladding (Silicon or Glass)
        # Layer 2: Holes (Etch layer)
        
        # 1. Draw the Cladding (Circle)
        cladding_radius = pitch * (geometry.rings + 1)
        cladding = gdstk.regular_polygon((0, 0), cladding_radius, 128, layer=1)
        self.cell.add(cladding)

        # 2. Draw the Hexagonal Hole Pattern
        for ring in range(1, geometry.rings + 1):
            for i in range(6 * ring):
                angle = i * (2 * np.pi / (6 * ring))
                x = ring * pitch * np.cos(angle)
                y = ring * pitch * np.sin(angle)
                
                # Add hole to the 'Etch' layer (Layer 2)
                hole = gdstk.regular_polygon((x, y), radius, 64, layer=2)
                self.cell.add(hole)

        # 3. Write binary file
        self.lib.write_gds(output_path)
        print(f"[GDSII] Industrial mask generated at: {output_path}")
        return output_path
