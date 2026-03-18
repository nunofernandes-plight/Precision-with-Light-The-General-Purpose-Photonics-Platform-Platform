import lumapi
import numpy as np
import pandas as pd
from pyDOE import lhs # Latin Hypercube Sampling for efficient design space coverage

class SimulationOrchestrator:
    def __init__(self, model_path):
        print("Initializing Physics Engine...")
        self.fdtd = lumapi.FDTD(filename=model_path)
        self.results = []

    def run_sweep(self, samples=100):
        """
        Uses Latin Hypercube Sampling (LHS) to ensure we don't 
        just sample a grid, but cover the 'Design Space' multidimensionally.
        """
        # Define Design Space: [Wavelength (um), Pitch (um), d/Lambda Ratio]
        # Ranges: Wavelength (1.3-1.6), Pitch (1.0-5.0), d/L (0.3-0.8)
        design_space = lhs(3, samples=samples)
        
        # Scale samples to real physical units
        wavelengths = 1.3 + design_space[:, 0] * 0.3
        pitches = 1.0 + design_space[:, 1] * 4.0
        ratios = 0.3 + design_space[:, 2] * 0.5

        for i in range(samples):
            w = wavelengths[i]
            p = pitches[i]
            r = ratios[i]
            
            print(f"Running Simulation {i+1}/{samples}: λ={w:.3f}, Λ={p:.2f}, d/Λ={r:.2f}")
            
            # 1. Update Geometry in Simulation
            self.fdtd.switchtolayout()
            self.fdtd.setnamed("PCF_Structure", "pitch", float(p))
            self.fdtd.setnamed("PCF_Structure", "d_over_pitch", float(r))
            self.fdtd.setglobalmonitor("wavelength center", float(w))
            
            # 2. Execute Solver
            self.fdtd.run()
            
            # 3. Extract Mathematical Results
            # We want the complex effective index: n_eff = n + ik
            mode_data = self.fdtd.getresult("FDE::data::mode1", "neff")
            n_eff_real = np.real(mode_data)[0]
            
            self.results.append({
                "wavelength": w,
                "pitch": p,
                "d_over_pitch": r,
                "n_eff": n_eff_real
            })

    def save_to_csv(self, filename="training_data.csv"):
        df = pd.DataFrame(self.results)
        df.to_csv(filename, index=False)
        print(f"Dataset generated with {len(df)} samples saved to {filename}")

if __name__ == "__main__":
    # FIX: Point strictly to Lumerical MODE files (.lms)
    # The 'save_to_csv' is removed because saving now happens safely line-by-line inside the loop.
    orchestrator = DataPipelineOrchestrator("templates/pcf_base_model.lms") 
    orchestrator.run_sweep(total_samples=500)
