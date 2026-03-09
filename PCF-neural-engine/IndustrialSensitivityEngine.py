import numpy as np
import pandas as pd
from typing import Dict, Any

class IndustrialSensitivityEngine:
    """
    Production-grade stochastic analyzer for PCF manufacturing resilience.
    Predicts how 2% drifts in geometry affect n_eff and TMI thresholds.
    """

    def __init__(self, model_wrapper: Any):
        # We inject the audited PCFModel instance here (Dependency Injection)
        self.model = model_wrapper

    def analyze_yield(
        self, 
        nominal_params: np.ndarray, 
        tolerance: float = 0.02, 
        iterations: int = 10000
    ) -> Dict[str, Any]:
        """
        Runs a vectorized Monte Carlo simulation to determine manufacturing yield.
        """
        # 1. Vectorized Noise Generation (Gaussian jitter)
        # Shape: (iterations, 3) -> [wavelength, pitch, d/L]
        noise = np.random.normal(1.0, tolerance, (iterations, 3))
        
        # We assume wavelength (idx 0) is stable, jitter only geometry (idx 1, 2)
        test_matrix = np.tile(nominal_params, (iterations, 1))
        test_matrix[:, 1:] *= noise[:, 1:]

        # 2. Batch Inference (The AI Advantage)
        # Using the audited predict_n_eff from your previous step
        try:
            predictions = self.model.predict_n_eff(test_matrix)
        except ValueError as e:
            return {"error": f"Stochastic jitter pushed parameters out of bounds: {e}"}

        # 3. Statistical Analysis
        mean_neff = np.mean(predictions)
        std_neff = np.std(predictions)
        
        # 4. Industrial Yield Calculation
        # Yield = % of fibers that stay within +/- 0.001 of target n_eff
        within_spec = np.abs(predictions - mean_neff) < 0.001
        yield_percentage = (np.sum(within_spec) / iterations) * 100

        return {
            "mean_neff": round(float(mean_neff), 6),
            "std_dev": round(float(std_neff), 8),
            "yield_at_1e_3_tolerance": f"{yield_percentage:.2f}%",
            "iterations": iterations
        }
