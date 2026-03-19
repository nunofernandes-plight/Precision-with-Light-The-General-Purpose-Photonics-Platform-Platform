import gdstk
import numpy as np
from ..1_intent_layer.schemas import WaveguideGeometry, PCFGeometry

class GDSIIExporter:
    """
    The 'Foundry Interface': Converts AI-synthesized parameters into 
    industry-standard GDSII lithography masks.
    """
    def __init__(self, lib_name: str = "PLIGHT_LIB"):
        self.lib = gdstk.Library(lib_name)
        self.cell = self.lib.new_cell("DEVICE_LAYOUT")

    def draw_pcf_cross_section(self, geometry: PCFGeometry, layer: int = 1):
        """Draws the hexagonal lattice for fiber preforms or facets."""
        pitch = geometry.pitch_um
        radius = (geometry.d_over_pitch * pitch) / 2
        
        # Draw Cladding
        cladding_r = pitch * (geometry.rings + 1)
        self.cell.add(gdstk.regular_polygon((0, 0), cladding_r, 128, layer=layer))

        # Draw Holes (Etch Layer)
        for r in range(1, geometry.rings + 1):
            for i in range(6 * r):
                angle = i * (2 * np.pi / (6 * r))
                x = r * pitch * np.cos(angle)
                y = r * pitch * np.sin(angle)
                self.cell.add(gdstk.regular_polygon((x, y), radius, 64, layer=layer+1))

    def draw_waveguide(self, geometry: WaveguideGeometry, length_um: float = 1000.0):
        """
        Draws a Silicon Waveguide bus. 
        Supports multi-layer exports for Rib waveguides (Layer 1: Core, Layer 2: Etch).
        """
        width = geometry.width_nm / 1000.0  # Convert nm to um for GDS standard
        
        # Layer 1: The Waveguide Bus (The 'Silicon' Layer)
        # We create a simple rectangular path
        bus = gdstk.RobustPath((0, 0), width, layer=1)
        bus.segment((length_um, 0))
        self.cell.add(bus)

        # If it's a Rib waveguide (etch_depth < height), we add the slab layer
        if geometry.etch_depth_nm < geometry.height_nm:
            slab_width = width + 4.0 # Standard 2um overhang on each side
            slab = gdstk.RobustPath((0, 0), slab_width, layer=2)
            slab.segment((length_um, 0))
            self.cell.add(slab)
            print(f"[GDSII] Rib Waveguide detected. Layers 1 & 2 generated.")
        else:
            print(f"[GDSII] Strip Waveguide detected. Layer 1 generated.")

    def finalize(self, output_path: str = "foundry_export.gds"):
        self.lib.write_gds(output_path)
        print(f"✅ GDSII Export Complete: {output_path}")
        return output_path


