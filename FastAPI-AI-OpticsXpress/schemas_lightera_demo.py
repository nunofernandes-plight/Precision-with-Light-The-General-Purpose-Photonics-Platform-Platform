from pydantic import BaseModel, Field
from typing import Optional

class FiberInput(BaseModel):
    # Core Geometry
    wavelength: float = Field(1.064, gt=0.3, lt=3.0, description="Operating wavelength in microns (e.g., 1.064 for Yb)")
    pitch: float = Field(20.0, gt=0.5, lt=100.0, description="Hole pitch or core-to-core distance in microns")
    d_over_pitch: float = Field(0.5, gt=0.05, lt=0.95, description="d/Lambda ratio (hole diameter / pitch)")

    # Thermal & Material Science (The Lightera Knobs)
    dn_dt: float = Field(
        1.1e-5, 
        description="Thermo-optic coefficient (K^-1). Standard Silica is ~1.1e-5. Try 0.8e-5 for TOC-optimized designs."
    )
    absorption_db_m: float = Field(
        0.35, 
        description="Cladding absorption in dB/m. Crucial for TMI threshold scaling."
    )

class FiberOutput(BaseModel):
    n_eff: float = Field(..., description="Effective index of the fundamental mode")
    mode_area_um2: float = Field(..., description="Effective Mode Area (A_eff) in square microns")
    v_parameter: float = Field(..., description="Calculated V_eff (Mortensen theory)")
    
    # Industrial KPIs
    tmi_threshold_kw: float = Field(..., description="Predicted Transverse Mode Instability threshold in Kilowatts")
    is_single_mode: bool = Field(..., description="True if V_eff < PI")
    is_tmi_safe_at_5kw: bool = Field(..., description="Reliability flag for Lightera-class 5.2kW benchmarks")
    
    status_message: str = Field(..., description="AI design recommendation based on physical constraints")
