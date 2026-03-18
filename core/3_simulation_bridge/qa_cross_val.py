import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from sklearn.metrics import mean_squared_error, r2_score

class CrossValidationQA:
    """
    Scientific Certification: Compares Lumerical vs. COMSOL datasets 
    to validate the 'Ground Truth' for the AI models.
    """
    def __init__(self, lumerical_path: str, comsol_path: str):
        self.df_lum = pd.read_csv(lumerical_path)
        self.df_com = pd.read_csv(comsol_path)
        
        # Ensure we are comparing the exact same geometric points
        self.merged = pd.merge(
            self.df_lum, self.df_com, 
            on=["wavelength_um", "pitch_um", "d_over_pitch"], 
            suffixes=('_lum', '_com')
        )

    def calculate_metrics(self):
        y_lum = self.merged['n_eff_lum']
        y_com = self.merged['n_eff_com']
        
        # Statistical Delta
        mae = np.mean(np.abs(y_lum - y_com))
        rmse = np.sqrt(mean_squared_error(y_lum, y_com))
        r2 = r2_score(y_lum, y_com)
        corr, _ = pearsonr(y_lum, y_com)

        print("-" * 30)
        print("QA CERTIFICATION REPORT")
        print("-" * 30)
        print(f"Samples Cross-Validated: {len(self.merged)}")
        print(f"Mean Absolute Error:    {mae:.6f}")
        print(f"RMSE:                   {rmse:.6f}")
        print(f"R² Correlation:         {r2:.6f}")
        print("-" * 30)
        
        if mae < 1e-4:
            print("STATUS: ✅ SCIENTIFICALLY CERTIFIED")
        else:
            print("STATUS: ⚠️ VARIANCE DETECTED (Check Mesh Settings)")

    def generate_plot(self, output_path: str = "qa_reports/validation_plot.png"):
        plt.figure(figsize=(8, 6))
        plt.scatter(self.merged['n_eff_lum'], self.merged['n_eff_com'], alpha=0.5)
        plt.plot([self.merged['n_eff_lum'].min(), self.merged['n_eff_lum'].max()],
                 [self.merged['n_eff_lum'].min(), self.merged['n_eff_lum'].max()], 
                 'r--', label='Perfect Agreement')
        plt.xlabel("n_eff (Lumerical FDE)")
        plt.ylabel("n_eff (COMSOL FEM)")
        plt.title("Cross-Solver Scientific Validation")
        plt.legend()
        plt.grid(True)
        plt.savefig(output_path)
        print(f"[QA] Validation plot saved to {output_path}")

if __name__ == "__main__":
    qa = CrossValidationQA("data/raw/training_data.csv", "data/raw/comsol_pcf_data.csv")
    qa.calculate_metrics()
    qa.generate_plot()
