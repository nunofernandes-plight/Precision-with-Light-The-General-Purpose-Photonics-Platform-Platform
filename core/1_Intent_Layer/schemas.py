from pydantic import BaseModel, Field, validator
from typing import Optional, Union
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
    """The 'Intent': What the user wants the light to do."""
    wavelength_nm: float = Field(..., gt=300, lt=4000)
    target_n_eff: Optional[float] = Field(None)
    max_dispersion: Optional[float] = Field(None)
    min_mode_area_um2: Optional[float] = Field(None)

class FabConstraints(BaseModel):
    """The 'Reality': Physical limits of the manufacturing hardware."""
    min_feature_size_nm: float = Field(200.0)
    max_aspect_ratio: float = Field(10.0)
    material_index: float = Field(1.444)

# --- COMPONENT SPECIFIC SCHEMAS ---

class PCFGeometry(BaseModel):
    """Physical parameters of a Photonic Crystal Fiber."""
    pitch_um: float = Field(..., ge=0.5, le=10.0)
    d_over_pitch: float = Field(..., ge=0.2, le=0.95)
    rings: int = Field(default=5, ge=1, le=10)

    @validator('d_over_pitch')
    def check_non_overlap(cls, v):
        if v >= 0.98:
            raise ValueError("Holes are overlapping; physical fabrication impossible.")
        return v

class WaveguideGeometry(BaseModel):
    """
    Physical parameters of an Integrated Silicon Waveguide.
    Supports both Strip (etch_depth == height) and Rib geometries.
    """
    width_nm: float = Field(..., ge=100.0, le=3000.0, description="Core width")
    height_nm: float = Field(220.0, ge=100.0, le=1000.0, description="Standard SOI thickness is usually 220nm or 300nm")
    etch_depth_nm: float = Field(..., ge=0.0)
    cladding_material: str = Field(default="SiO2", description="Top cladding (e.g., Air, SiO2, Si3N4)")

    @validator('etch_depth_nm')
    def check_physical_etch(cls, v, values):
        """Physics Guardrail: You cannot etch deeper than the silicon layer itself."""
        if 'height_nm' in values and v > values['height_nm']:
            raise ValueError(f"Fabrication Error: Etch depth ({v}nm) exceeds core height ({values['height_nm']}nm).")
        return v

# --- THE UNIFIED REQUEST ---

class DesignRequest(BaseModel):
    request_id: str
    component_type: ComponentType
    method: ManufacturingMethod
    targets: OpticalTargets
    constraints: Optional[FabConstraints] = FabConstraints()
    metadata: Optional[dict] = {"priority": "low_latency"}

class DesignResponse(BaseModel):
    request_id: str
    status: str = "success"
    # The API can now return EITHER a Fiber or a Waveguide!
    suggested_geometry: Union[PCFGeometry, WaveguideGeometry, dict] 
    confidence_score: float = Field(..., ge=0, le=1.0)
    validation_status: str
