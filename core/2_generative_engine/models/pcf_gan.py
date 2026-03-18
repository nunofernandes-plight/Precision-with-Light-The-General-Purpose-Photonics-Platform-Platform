import torch
from .architecture import Generator # Assuming your audited classes are here
from ...1_intent_layer.schemas import OpticalTargets, PCFGeometry

class PCFGenerativeService:
    """
    The 'Engine Room': Consumes Optical Targets, 
    Synthesizes validated Geometry.
    """
    def __init__(self, model_path: str):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = Generator(input_dim=10, output_dim=2) # Audited Arch
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()

    def synthesize(self, targets: OpticalTargets) -> PCFGeometry:
        # 1. Prepare latent vector + conditional targets
        # [λ, n_eff, etc.] -> Tensor
        input_tensor = torch.tensor([[targets.wavelength_nm, targets.target_n_eff]], dtype=torch.float32)
        
        with torch.no_grad():
            prediction = self.model(input_tensor).numpy()[0]
        
        # 2. Map AI output to our Pydantic Schema
        # Prediction[0] = Pitch, Prediction[1] = d/pitch
        geometry = PCFGeometry(
            pitch_um=float(prediction[0]),
            d_over_pitch=float(prediction[1]),
            rings=5 # Default for this model version
        )
        
        print(f"[Engine] Generated Design: Pitch={geometry.pitch_um:.2f}um, d/Λ={geometry.d_over_pitch:.2f}")
        return geometry
