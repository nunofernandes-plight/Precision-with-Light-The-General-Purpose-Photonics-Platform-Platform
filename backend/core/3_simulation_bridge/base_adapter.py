# backend/3_simulation_bridge/base_adapter.py

from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel
import numpy as np


class SimulationInput(BaseModel):
    """Unified geometry representation from the Generative Engine."""
    design_family: str          # "lma_fiber" | "hc_pcf" | "si_photonics" | "si3n4"
    geometry_tensor: list       # Serialized geometry from cWGAN-GP output
    wavelength_range_nm: tuple[float, float]
    target_metrics: list[str]   # e.g. ["neff", "loss_db_per_m", "s_params"]
    pdk_node: Optional[str]     # e.g. "AIM_PDK_300mm" for silicon photonics
    simulation_fidelity: str    # "fast" | "standard" | "high"


class SimulationResult(BaseModel):
    """Unified result schema returned by every adapter."""
    adapter: str                # "lumerical" | "comsol" | "tidy3d"
    passed_fidelity_check: bool
    fidelity_score: float       # 0.0–1.0 vs. DSR-CRAG prediction
    neff_real: Optional[float]
    neff_imag: Optional[float]
    loss_db_per_m: Optional[float]
    mode_area_um2: Optional[float]
    s_parameters: Optional[dict]     # S11, S21 etc. for PIC components
    field_profile: Optional[np.ndarray]
    compute_time_seconds: float
    solver_version: str
    raw_output_path: Optional[str]   # Path to full solver output archive


class SimulationAdapter(ABC):
    """Abstract base — all adapters must implement these three methods."""

    @abstractmethod
    def validate_input(self, sim_input: SimulationInput) -> bool:
        """Pre-flight check: can this adapter handle the design family?"""
        ...

    @abstractmethod
    def submit(self, sim_input: SimulationInput) -> str:
        """Submit simulation job. Returns job_id for async polling."""
        ...

    @abstractmethod
    def retrieve(self, job_id: str) -> SimulationResult:
        """Poll and retrieve completed simulation result."""
        ...



