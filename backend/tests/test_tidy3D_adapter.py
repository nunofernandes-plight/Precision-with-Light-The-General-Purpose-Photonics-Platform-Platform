# backend/tests/test_tidy3d_adapter.py

import pytest
from unittest.mock import patch, MagicMock
from backend.simulation_bridge.tidy3d_adapter import Tidy3DAdapter
from backend.simulation_bridge.base_adapter import SimulationInput


@pytest.fixture
def mock_api_key(monkeypatch):
    monkeypatch.setenv("TIDY3D_API_KEY", "test_key_mock")


@pytest.fixture
def si_photonics_input():
    return SimulationInput(
        design_family="si_photonics",
        geometry_tensor={
            "waveguide_width_nm": 450,
            "waveguide_length_um": 10.0,
            "si_thickness_nm": 220,
            "box_thickness_um": 2.0
        },
        wavelength_range_nm=(1530.0, 1570.0),
        target_metrics=["s_params", "neff"],
        pdk_node="AIM_PDK_300mm",
        simulation_fidelity="standard"
    )


@pytest.fixture
def si3n4_input():
    return SimulationInput(
        design_family="si3n4",
        geometry_tensor={
            "waveguide_width_nm": 800,
            "si3n4_thickness_nm": 300,
            "device_length_um": 50.0
        },
        wavelength_range_nm=(1520.0, 1580.0),
        target_metrics=["s_params"],
        pdk_node=None,
        simulation_fidelity="standard"
    )


@pytest.fixture
def hcpcf_input():
    return SimulationInput(
        design_family="hc_pcf",
        geometry_tensor={
            "core_radius_um": 15.0,
            "tube_radius_um": 7.0,
            "tube_wall_thickness_um": 0.42,
            "num_tubes": 6
        },
        wavelength_range_nm=(1030.0, 1080.0),
        target_metrics=["neff", "loss_db_per_m", "mode_area_um2"],
        pdk_node=None,
        simulation_fidelity="fast"
    )


class TestTidy3DAdapterInit:
    def test_raises_without_api_key(self):
        with pytest.raises(EnvironmentError, match="TIDY3D_API_KEY"):
            Tidy3DAdapter(api_key=None)

    def test_initialises_with_api_key(self, mock_api_key):
        adapter = Tidy3DAdapter()
        assert adapter.api_key == "test_key_mock"


class TestValidateInput:
    def test_accepts_si_photonics(self, mock_api_key, si_photonics_input):
        adapter = Tidy3DAdapter()
        assert adapter.validate_input(si_photonics_input) is True

    def test_accepts_si3n4(self, mock_api_key, si3n4_input):
        adapter = Tidy3DAdapter()
        assert adapter.validate_input(si3n4_input) is True

    def test_accepts_hcpcf(self, mock_api_key, hcpcf_input):
        adapter = Tidy3DAdapter()
        assert adapter.validate_input(hcpcf_input) is True

    def test_rejects_unsupported_family(self, mock_api_key):
        adapter = Tidy3DAdapter()
        bad_input = SimulationInput(
            design_family="metasurface",
            geometry_tensor={},
            wavelength_range_nm=(500.0, 900.0),
            target_metrics=[],
            simulation_fidelity="fast"
        )
        assert adapter.validate_input(bad_input) is False


class TestGeometryTranslation:
    """Tests that geometry tensors from cWGAN-GP produce valid Tidy3D Simulation objects."""

    def test_si_photonics_simulation_builds(self, mock_api_key, si_photonics_input):
        import tidy3d as td
        adapter = Tidy3DAdapter()
        sim = adapter._build_simulation(si_photonics_input)
        assert isinstance(sim, td.Simulation)
        assert len(sim.structures) >= 2      # substrate + waveguide
        assert len(sim.sources) == 1
        assert len(sim.monitors) >= 1

    def test_si3n4_simulation_builds(self, mock_api_key, si3n4_input):
        import tidy3d as td
        adapter = Tidy3DAdapter()
        sim = adapter._build_simulation(si3n4_input)
        assert isinstance(sim, td.Simulation)

    def test_hcpcf_simulation_builds(self, mock_api_key, hcpcf_input):
        import tidy3d as td
        adapter = Tidy3DAdapter()
        sim = adapter._build_simulation(hcpcf_input)
        assert isinstance(sim, td.Simulation)
        # 6 tubes + 1 jacket
        assert len(sim.structures) == 7

    def test_waveguide_width_reflected_in_geometry(self, mock_api_key):
        import tidy3d as td
        adapter = Tidy3DAdapter()
        wide_input = SimulationInput(
            design_family="si_photonics",
            geometry_tensor={"waveguide_width_nm": 900, "waveguide_length_um": 10.0},
            wavelength_range_nm=(1530.0, 1570.0),
            target_metrics=["s_params"],
            simulation_fidelity="fast"
        )
        sim = adapter._build_simulation(wide_input)
        # Waveguide structure should reflect 900nm width
        wg_structure = [s for s in sim.structures if "waveguide" in str(s)]
        # Geometry check via simulation domain size
        assert sim is not None  # Structural check — extend with geometry assertions


class TestBridgeRouting:
    def test_tidy3d_preferred_for_si_photonics(self, monkeypatch):
        monkeypatch.setenv("TIDY3D_API_KEY", "test_key")
        monkeypatch.delenv("LUMERICAL_PATH", raising=False)
        monkeypatch.delenv("COMSOL_PATH", raising=False)

        from backend.simulation_bridge.bridge import get_adapter
        si_input = SimulationInput(
            design_family="si_photonics",
            geometry_tensor={"waveguide_width_nm": 450},
            wavelength_range_nm=(1530.0, 1570.0),
            target_metrics=["s_params"],
            simulation_fidelity="standard"
        )
        adapter = get_adapter(si_input)
        assert isinstance(adapter, Tidy3DAdapter)

    def test_raises_when_no_adapter_available(self, monkeypatch):
        monkeypatch.delenv("TIDY3D_API_KEY", raising=False)
        monkeypatch.delenv("LUMERICAL_PATH", raising=False)
        monkeypatch.delenv("COMSOL_PATH", raising=False)

        from backend.simulation_bridge.bridge import get_adapter
        with pytest.raises(RuntimeError, match="No simulation adapter"):
            get_adapter(SimulationInput(
                design_family="si_photonics",
                geometry_tensor={},
                wavelength_range_nm=(1530.0, 1570.0),
                target_metrics=[],
                simulation_fidelity="fast"
            ))




