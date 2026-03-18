from pydantic import BaseModel, Field, validator
from typing import List, Optional, Union
from enum import Enum

class ComponentType(str, Enum):
    PCF = "photonic_crystal_fiber"
    WAVEGUIDE = "integrated_waveguide"
    METASURFACE = "metasurface"

class ManufacturingMethod(str, Enum):
    NANOSCRIBE_2PP = "nanoscribe_2pp"
    SILICON_FOUNDRY = "silicon_foundry"
    MCVD = "mcvd_stacking"

# --- CORE CONTRACTS ---

class OpticalTargets(BaseModel):
    """
    The 'Intent': What the user wants the light to do.
    """
    wavelength_nm: float = Field(..., gt=300, lt=4000, description="Operating wavelength in nanometers")
    target_n_eff: Optional[float] = Field(None, description="Target effective refractive index")
    max_dispersion: Optional[float] = Field(None, description="Maximum allowable dispersion (ps/nm/km)")
    min_mode_area_um2: Optional[float] = Field(None, description="Minimum effective mode area")

class FabConstraints(BaseModel):
    """
    The 'Reality': Physical limits of the manufacturing hardware.
    """
    min_feature_size_nm: float = Field(200.0, description="Minimum resolution of the printer/lithography")
    max_aspect_ratio: float = Field(10.0, description="Max depth-to-width ratio for holes/pillars")
    material_index: float = Field(1.444, description="Refractive index of the substrate/glass")

# --- COMPONENT SPECIFIC SCHEMAS ---

class PCFGeometry(BaseModel):
    """
    The 'Design': The physical parameters of a Photonic Crystal Fiber.
    """
    pitch_um: float = Field(..., ge=0.5, le=10.0)
    d_over_pitch: float = Field(..., ge=0.2, le=0.95)
    rings: int = Field(default=5, ge=1, le=10)

    @validator('d_over_pitch')
    def check_non_overlap(cls, v):
        if v >= 0.98:
            raise ValueError("Holes are overlapping; physical fabrication impossible.")
        return v

# --- THE UNIFIED REQUEST ---

class DesignRequest(BaseModel):
    """
    The Master Entry Point: This is what the Partner sends to your API.
    """
    request_id: str
    component_type: ComponentType
    method: ManufacturingMethod
    targets: OpticalTargets
    constraints: Optional[FabConstraints] = FabConstraints()
    
    # This allows the AI to return multiple 'candidate' designs
    metadata: Optional[dict] = {"priority": "low_latency"}

class DesignResponse(BaseModel):
    """
    What the Platform returns to the Partner.
    """
    request_id: str
    status: str = "success"
    suggested_geometry: Union[PCFGeometry, dict]
    confidence_score: float = Field(..., ge=0, le=1.0)
    validation_status: str # e.g., "AI_ONLY" or "SOLVER_VERIFIED"
