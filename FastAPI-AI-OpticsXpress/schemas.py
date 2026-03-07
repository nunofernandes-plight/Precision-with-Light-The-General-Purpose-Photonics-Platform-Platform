from pydantic import BaseModel, Field

class FiberInput(BaseModel):
    wavelength: float = Field(..., gt=0.3, lt=3.0, description="Wavelength in microns")
    pitch: float = Field(..., gt=0.5, lt=10.0, description="Hole pitch in microns")
    d_over_pitch: float = Field(..., gt=0.1, lt=0.9, description="d/Lambda ratio")

class FiberOutput(BaseModel):
    n_eff_real: float
    dispersion: float
    mode_area: float
    v_parameter: float
    is_single_mode: bool 
