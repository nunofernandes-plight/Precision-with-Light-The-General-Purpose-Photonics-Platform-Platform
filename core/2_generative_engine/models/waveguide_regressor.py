import torch
import torch.nn as nn
from typing import Dict
from ...1_intent_layer.schemas import WaveguideGeometry, OpticalTargets

class WaveguideMLP(nn.Module):
    """
    The Core Neural Architecture for Silicon Photonics (Forward Model).
    Takes a 4D input [width, height, etch_depth, cladding_index] 
    and predicts a 2D output [n_eff, dispersion].
    """
    def __init__(self, input_dim: int = 4, hidden_dim: int = 128, output_dim: int = 2):
        super(WaveguideMLP, self).__init__()
        
        # Enterprise-grade MLP: LayerNorm stabilizes training for varied geometric scales
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(), # GELU often outperforms ReLU in continuous physics regressions
            
            nn.Linear(hidden_dim, hidden_dim * 2),
            nn.LayerNorm(hidden_dim * 2),
            nn.GELU(),
            
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            
            nn.Linear(hidden_dim, output_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)

class WaveguidePredictorService:
    """
    The 'Service Wrapper' that connects the raw PyTorch math to our API Schemas.
    """
    def __init__(self, model_weights_path: str = None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = WaveguideMLP().to(self.device)
        
        # In production, we load the trained .pt file here.
        if model_weights_path:
            try:
                self.model.load_state_dict(torch.load(model_weights_path, map_location=self.device))
                self.model.eval()
                print(f"[Engine] Silicon Waveguide Engine loaded from {model_weights_path}")
            except FileNotFoundError:
                print("[Engine] Warning: Weights not found. Running with initialized random weights.")

    def _cladding_to_index(self, material_name: str) -> float:
        """Helper to convert string materials to baseline refractive indices."""
        indices = {"Air": 1.0, "SiO2": 1.444, "Si3N4": 2.0}
        return indices.get(material_name, 1.444) # Default to oxide cladding

    def predict_performance(self, geometry: WaveguideGeometry, wavelength_nm: float = 1550.0) -> OpticalTargets:
        """
        Instantly predicts optical targets from the physical geometry.
        Bypasses traditional FEM solvers (Lumerical/COMSOL).
        """
        # 1. Map the Pydantic schema to a PyTorch Tensor
        cladding_idx = self._cladding_to_index(geometry.cladding_material)
        
        # Inputs must be normalized in a real training scenario. 
        # Represented here as raw values for architectural clarity.
        input_tensor = torch.tensor([[
            geometry.width_nm, 
            geometry.height_nm, 
            geometry.etch_depth_nm, 
            cladding_idx
        ]], dtype=torch.float32).to(self.device)

        # 2. Run Inference
        with torch.no_grad():
            prediction = self.model(input_tensor).cpu().numpy()[0]

        # 3. Map AI output back to the Pydantic API response
        # Assuming prediction[0] = n_eff, prediction[1] = dispersion
        predicted_targets = OpticalTargets(
            wavelength_nm=wavelength_nm,
            target_n_eff=float(prediction[0]),
            max_dispersion=float(prediction[1])
        )

        return predicted_targets


