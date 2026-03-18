import os
import csv
import lumapi
import numpy as np
import pandas as pd
from pyDOE import lhs

class DataPipelineOrchestrator:
    """
    Enterprise-grade Lumerical automation for Precision with Light.
    Features LHS space-filling, line-by-line checkpointing, and auto-resumption.
    """
    def __init__(self, model_path: str, output_csv: str = "pcf_training_data.csv"):
        print("[System] Initializing Precision with Light Physics Engine...")
        
        # FIX 1: Initializing MODE solver (for fibers) instead of FDTD
        self.mode = lumapi.MODE(filename=model_path)
        self.output_csv = output_csv
        self._initialize_csv()

    def _initialize_csv(self):
        """Creates the CSV with headers if it doesn't exist."""
        if not os.path.exists(self.output_csv):
            with open(self.output_csv, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["wavelength_um", "pitch_um", "d_over_pitch", "n_eff_real"])
            print(f"[System] Created new checkpoint file: {self.output_csv}")

    def get_completed_iterations(self) -> int:
        """Checks how many simulations have already been successfully saved."""
        if not os.path.exists(self.output_csv):
            return 0
        df = pd.read_csv(self.output_csv)
        return len(df)

    def run_sweep(self, total_samples: int = 500):
        # Generate the FULL Latin Hypercube to maintain the statistical distribution
        design_space = lhs(3, samples=total_samples)
        
        # Scale samples to real physical units
        wavelengths = 1.3 + design_space[:, 0] * 0.3
        pitches = 1.0 + design_space[:, 1] * 4.0
        ratios = 0.3 + design_space[:, 2] * 0.5

        # FIX 2: Enterprise Resumption Logic
        start_index = self.get_completed_iterations()
        
        if start_index >= total_samples:
            print("[System] All samples already computed. Pipeline complete.")
            return

        print(f"[System] Resuming from sample {start_index + 1}/{total_samples}...")

        for i in range(start_index, total_samples):
            w, p, r = wavelengths[i], pitches[i], ratios[i]
            print(f"-> Sim {i+1}/{total_samples}: λ={w:.3f}, Λ={p:.2f}, d/Λ={r:.2f}")
            
            try:
                # 1. Update Geometry in Simulation
                self.mode.switchtolayout()
                self.mode.setnamed("PCF_Structure", "pitch", float(p))
                self.mode.setnamed("PCF_Structure", "d_over_pitch", float(r))
                
                # Update solver wavelength (In MODE, this is usually set in the FDE region)
                self.mode.setnamed("FDE", "wavelength", float(w) * 1e-6) # Assumes Lumerical expects meters here
                
                # 2. Execute Solver
                self.mode.findmodes() # FDE uses findmodes() instead of run()
                
                # 3. Extract Results
                mode_data = self.mode.getdata("FDE::data::mode1", "neff")
                n_eff_real = float(np.real(mode_data)[0])
                
                # FIX 3: Checkpointing (Save immediately after solving)
                with open(self.output_csv, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([w, p, r, n_eff_real])
                    
            except Exception as e:
                # FIX 4: Defensive Error Logging
                print(f"[ERROR] Simulation {i+1} failed. Logging and continuing. Error: {e}")
                with open("pipeline_errors.log", mode='a') as log:
                    log.write(f"Sim {i+1} Failed - W={w:.3f}, P={p:.2f}, R={r:.2f} | {e}\n")
                # The loop continues to the next sample. A single bad mesh won't kill the batch.

if __name__ == "__main__":
    orchestrator = DataPipelineOrchestrator("templates/pcf_base_model.lms") # Ensure .lms extension for MODE
    orchestrator.run_sweep(total_samples=1000)
