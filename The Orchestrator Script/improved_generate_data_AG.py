import lumapi
import numpy as np
import pandas as pd
import csv
import os
from scipy.stats import qmc

class SimulationOrchestrator:
    def __init__(self, model_path, output_filename="training_data.csv"):
        print("Initializing Physics Engine...")
        self.engine = lumapi.FDTD(filename=model_path, hide=False)
        self.output_filename = output_filename
        
        # Define the columns we will track
        self.fields = ["run_id", "wavelength", "pitch", "d_over_pitch", "n_eff", "status"]
        self._initialize_checkpoint_file()

    def _initialize_checkpoint_file(self):
        """
        Creates the CSV file and writes the header if it doesn't exist.
        If it exists (e.g., resuming a run), it leaves it alone.
        """
        file_exists = os.path.isfile(self.output_filename)
        
        # 'a' mode appends to the file, creating it if it doesn't exist
        with open(self.output_filename, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.fields)
            if not file_exists:
                writer.writeheader()

    def _save_checkpoint(self, data_row):
        """Instantly saves a single simulation's result to the hard drive."""
        with open(self.output_filename, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.fields)
            writer.writerow(data_row)

    def close(self):
        """Safely close the Lumerical engine to free up the license."""
        if hasattr(self, 'engine'):
            self.engine.close()

    def run_sweep(self, samples=100):
        # Modern SciPy LHS generator
        sampler = qmc.LatinHypercube(d=3)
        design_space = sampler.random(n=samples)
        
        # Scale parameters
        wavelengths = 1.3 + design_space[:, 0] * (1.6 - 1.3)
        pitches = 1.0 + design_space[:, 1] * (5.0 - 1.0)
        ratios = 0.3 + design_space[:, 2] * (0.8 - 0.3)

        print(f"Starting sweep of {samples} samples. Data streams safely to {self.output_filename}")

        for i in range(samples):
            w = float(wavelengths[i])
            p = float(pitches[i])
            r = float(ratios[i])
            run_id = i + 1
            
            print(f"[{run_id}/{samples}] Simulating: λ={w:.3f}, Λ={p:.2f}, d/Λ={r:.2f}")
            
            # Prepare a default row in case of failure
            row = {
                "run_id": run_id,
                "wavelength": w, 
                "pitch": p, 
                "d_over_pitch": r,
                "n_eff": None, 
                "status": "failed"
            }
            
            try:
                # 1. Update Geometry
                self.engine.switchtolayout()
                self.engine.setnamed("PCF_Structure", "pitch", p)
                self.engine.setnamed("PCF_Structure", "d_over_pitch", r)
                self.engine.setglobalmonitor("wavelength center", w)
                
                # 2. Execute Solver
                self.engine.run()
                
                # 3. Extract Data
                mode_data = self.engine.getresult("FDE::data::mode1", "neff")
                n_eff_real = float(np.real(np.atleast_1d(mode_data).flatten()[0]))
                
                # Update row with success data
                row["n_eff"] = n_eff_real
                row["status"] = "success"
                
            except Exception as e:
                print(f"  -> Run {run_id} failed: {e}")
            
            finally:
                # 4. Save to Disk IMMEDIATELY. 
                # This guarantees that even if the next iteration crashes Python entirely, 
                # this iteration's data is already physically written to the hard drive.
                self._save_checkpoint(row)

if __name__ == "__main__":
    # Point this to your Lumerical file
    orchestrator = SimulationOrchestrator(
        model_path="templates/pcf_base_model.fsp", 
        output_filename="training_data.csv"
    )
    
    try:
        orchestrator.run_sweep(samples=500)
    finally:
        # We no longer need the Pandas bulk dump, just close the application!
        orchestrator.close()
        print("Simulation complete and Lumerical engine securely closed.")
