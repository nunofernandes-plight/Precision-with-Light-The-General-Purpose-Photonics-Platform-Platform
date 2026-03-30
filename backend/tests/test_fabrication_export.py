"""
Tests for the Fabrication Export module.
Validates GDSII generation, STL export, and fiber draw specifications.
"""
import pytest
import os
import tempfile
 
 
class TestGDSIIExporter:
    def test_gdsii_file_created(self, si_photonics_geometry, tmp_path):
        from backend._4_fabrication_export.gdsii_exporter import GDSIIExporter
 
        exporter = GDSIIExporter(pdk_node="AIM_PDK_300mm")
        output_path = tmp_path / "test_waveguide.gds"
        exporter.export(si_photonics_geometry, str(output_path))
 
        assert output_path.exists()
        assert output_path.stat().st_size > 0
 
    def test_gdsii_contains_correct_layers(self, si_photonics_geometry, tmp_path):
        """AIM PDK uses specific GDS layer numbers for each material."""
        import gdstk
        from backend._4_fabrication_export.gdsii_exporter import GDSIIExporter
 
        exporter    = GDSIIExporter(pdk_node="AIM_PDK_300mm")
        output_path = tmp_path / "waveguide.gds"
        exporter.export(si_photonics_geometry, str(output_path))
 
        lib = gdstk.read_gds(str(output_path))
        layers_used = set()
        for cell in lib.cells:
            for polygon in cell.polygons:
                layers_used.add(polygon.layer)
 
        # AIM PDK: Si waveguide on layer 1, BOX on layer 2
        assert 1 in layers_used  # Si core layer
 
    def test_gdsii_respects_drc_minimum_width(self, tmp_path):
        """Generated GDS polygons must not violate AIM minimum width of 400nm."""
        import gdstk
        from backend._4_fabrication_export.gdsii_exporter import GDSIIExporter
 
        narrow_geometry = {
            "design_family": "si_photonics",
            "waveguide_width_nm": 450,   # Valid: > 400nm minimum
            "waveguide_length_um": 10.0,
            "pdk_node": "AIM_PDK_300mm"
        }
        exporter    = GDSIIExporter(pdk_node="AIM_PDK_300mm")
        output_path = tmp_path / "drc_test.gds"
        exporter.export(narrow_geometry, str(output_path))
 
        lib = gdstk.read_gds(str(output_path))
        for cell in lib.cells:
            for polygon in cell.polygons:
                # Check bounding box width
                bbox = polygon.bounding_box()
                width_nm = (bbox[1][0] - bbox[0][0]) * 1000   # µm → nm
                if polygon.layer == 1:  # Si layer
                    assert width_nm >= 400
 
 
class TestSTLExporter:
    def test_stl_file_created(self, hcpcf_ar_geometry, tmp_path):
        from backend._4_fabrication_export.stl_exporter import STLExporter
 
        exporter    = STLExporter(fabrication_method="two_photon_polymerization")
        output_path = tmp_path / "hcpcf.stl"
        exporter.export(hcpcf_ar_geometry, str(output_path))
 
        assert output_path.exists()
        assert output_path.stat().st_size > 0
 
    def test_stl_minimum_feature_size(self, hcpcf_ar_geometry, tmp_path):
        """2PP minimum feature size is ~150nm — tube walls must exceed this."""
        from backend._4_fabrication_export.stl_exporter import STLExporter
 
        exporter = STLExporter(fabrication_method="two_photon_polymerization")
        # tube_wall_thickness_um = 0.42 µm = 420nm > 150nm minimum → should pass
        output_path = tmp_path / "test.stl"
        result = exporter.export(hcpcf_ar_geometry, str(output_path))
        assert result.drc_passed is True
 
 
class TestFiberDrawSpec:
    def test_draw_spec_generated(self, lma_comb_geometry, tmp_path):
        from backend._4_fabrication_export.draw_spec_exporter import DrawSpecExporter
 
        exporter    = DrawSpecExporter()
        output_path = tmp_path / "draw_spec.json"
        exporter.export(lma_comb_geometry, str(output_path))
 
        import json
        with open(output_path) as f:
            spec = json.load(f)
 
        assert "preform_design" in spec
        assert "draw_parameters" in spec
        assert "target_geometry" in spec
 
    def test_draw_spec_cvd_constraints(self, lma_comb_geometry):
        """CVD fabrication: index delta must be achievable with Ge doping."""
        from backend._4_fabrication_export.draw_spec_exporter import DrawSpecExporter
 
        exporter = DrawSpecExporter()
        spec = exporter.generate_spec(lma_comb_geometry)
 
        # peak_index_delta = 0.008 → achievable with ~5% Ge doping in silica
        assert spec["preform_design"]["ge_doping_percent"] < 15.0
        assert spec["preform_design"]["index_delta"] == pytest.approx(0.008, rel=0.01)


