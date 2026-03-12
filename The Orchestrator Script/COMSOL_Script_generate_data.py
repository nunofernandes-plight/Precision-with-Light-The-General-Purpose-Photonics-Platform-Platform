import os
import csv
import mph
import numpy as np
import pandas as pd
from pyDOE import lhs

class ComsolDataOrchestrator:
    """
    High-fidelity COMSOL Multiphysics automation for PCF Thermal-Optical analysis.
    Supports .mph files and ensures line-by-line data persistence.
    """
    def __init__(self, model_path: str, output_csv: str = "comsol_pcf_data.csv"):
        print("[System] Connecting to COMSOL Server...")
        
        # FIX 1: Start COMSOL Client (Requires COMSOL installation on local machine)
        self.client = mph.start() 
        self.model = self.client.load(model_path)
        self.output_csv = output_csv
        
        # Ensure the model is set up for Mode Analysis
        self._initialize_csv()

    def _initialize_csv(self):
        if not os.path.exists(self.output_csv):
            with open(self.output_csv, mode='w', newline='') as file:
                writer = csv.writer(file)
                # We add 'effective_area' as COMSOL calculates this easily
                writer.writerow(["wavelength_um", "pitch_um", "d_over_pitch", "n_eff_real", "mode_area"])
            print(f"[System] Created COMSOL checkpoint: {self.output_csv}")

    def get_progress(self) -> int:
        if not os.path.exists(self.output_csv): return 0
        return len(pd.read_csv(self.output_csv))

    def run_sweep(self, total_samples: int = 500):
        # Generate Design Space (LHS)
        design_space = lhs(3, samples=total_samples)
        wavelengths = 1.3 + design_space[:, 0] * 0.3
        pitches = 1.0 + design_space[:, 1] * 4.0
        ratios = 0.3 + design_space[:, 2] * 0.5

        start_idx = self.get_progress()
        print(f"[System] Resuming COMSOL study from {start_idx + 1}/{total_samples}")

        for i in range(start_idx, total_samples):
            w, p, r = wavelengths[i], pitches[i], ratios[i]
            
            try:
                # 1. Update Parameters (COMSOL uses strings for units)
                # We assume your .mph file has these Global Parameters defined
                self.model.parameter('wl_microns', f'{w} [um]')
                self.model.parameter('pitch_microns', f'{p} [um]')
                self.model.parameter('d_ratio', str(r))
                
                # 2. Re-mesh and Solve
                # Crucial: COMSOL geometry must be rebuilt if pitch changes
                self.model.mesh() 
                self.model.solve() 
                
                # 3. Extract Results
                # 'ewfd.neff' is the standard variable for Electromagnetics Mode Analysis
                n_eff_complex = self.model.evaluate('ewfd.neff')
                n_eff_real = np.real(n_eff_complex)
                
                # Extracting Effective Mode Area (Lightera's Key KPI)
                # Uses an integration variable you must define in COMSOL
                a_eff = self.model.evaluate('int_mode_area') 

                # 4. Checkpoint Save
                with open(self.output_csv, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([w, p, r, float(n_eff_real), float(a_eff)])
                
                print(f"Success: Sim {i+1} | neff: {n_eff_real:.5f}")

            except Exception as e:
                print(f"[CRITICAL ERROR] Sim {i+1} failed: {e}")
                continue

if __name__ == "__main__":
    # Point to your actual COMSOL Multiphysics binary
    orchestrator = ComsolDataOrchestrator("templates/pcf_core_model.mph")
    orchestrator.run_sweep(total_samples=250)
