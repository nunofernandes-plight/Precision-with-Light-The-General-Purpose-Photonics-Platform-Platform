import numpy as np
import joblib

class AIPlusPhysicsEngine:
    def __init__(self, model_path):
        # Load the trained PINN/Regressor weights
        # Our model now predicts neff, Mode Area (Aeff), and Confinement Loss
        self.model, self.scaler_x, self.scaler_y = joblib.load(model_path)
        
        # Physical Constants for Silica
        self.C_TMI = 1.4e-1  # Empirical scaling constant for Yb-doped fibers
        self.default_dn_dt = 1.1e-5  # Standard Silica TOC (K^-1)

    def predict_with_tmi(self, wavelength, pitch, d_lambda, dn_dt=None, absorption_db_m=0.35):
        """
        wavelength: microns
        pitch: microns
        d_lambda: d/Lambda ratio
        dn_dt: Thermo-optic coefficient (Customizable for Lightera TOC optimization)
        absorption_db_m: Cladding absorption (e.g., Lightera's 0.35 dB/m)
        """
        if dn_dt is None:
            dn_dt = self.default_dn_dt

        # 1. AI Inference: Get optical properties
        # test_input = [wavelength, pitch, d_lambda]
        X_scaled = self.scaler_x.transform([[wavelength, pitch, d_lambda]])
        preds = self.model.predict(X_scaled)
        unscaled_preds = self.scaler_y.inverse_transform(preds)[0]
        
        # Mapping predicted outputs (assumes specific index in Y_scaler)
        n_eff = unscaled_preds[0]
        a_eff = unscaled_preds[1]  # Effective Mode Area in um^2

        # 2. Physics Layer: Simplified TMI Threshold Calculation
        # The TMI threshold scales with: A_eff / (absorption * dn/dT)
        # Reference: Smith & Smith, "Mode instability in high power fiber amplifiers"
        
        # Convert A_eff to m^2 and absorption to m^-1
        a_eff_m2 = a_eff * 1e-12
        alpha_m = absorption_db_m / 4.343  # Conversion from dB/m to 1/m
        
        # TMI Threshold Formula (Simplified for real-time API response)
        # P_tmi ~ (lambda^2 * A_eff) / (dn_dt * alpha)
        p_tmi_kw = self.C_TMI * ( (wavelength * 1e-6)**2 * a_eff_m2 ) / (dn_dt * alpha_m)
        p_tmi_kw *= 1e15 # Scale factor for kW units

        # 3. Mode Stability Logic (The Pi-Cutoff)
        # Using neff_fsm from a secondary AI head or lookup
        neff_fsm = n_eff - 0.005 # Placeholder delta for demonstration
        v_eff = (2 * np.pi * pitch / wavelength) * np.sqrt(n_eff**2 - neff_fsm**2)

        return {
            "n_eff": float(n_eff),
            "mode_area_um2": float(a_eff),
            "v_parameter": float(v_eff),
            "is_single_mode": bool(v_eff < np.pi),
            "tmi_threshold_kw": round(float(p_tmi_kw), 2),
            "toc_used": dn_dt
        }
