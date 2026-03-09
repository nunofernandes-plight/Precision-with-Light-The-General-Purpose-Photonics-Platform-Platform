import joblib
import numpy as np

class PCFModel:
    def __init__(self, model_path="models/final_mlp.pkl", scaler_path="models/scaler.pkl"):
        # Load the trained model and the scaler used during training
        self.engine = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)

    def predict_n_eff(self, params):
        """
        params: array-like of shape (n_samples, 3) 
        [wavelength, pitch, d_over_pitch]
        """
        # Ensure input is 2D
        data = np.atleast_2d(params)
        scaled_data = self.scaler.transform(data) #([[wavelength, pitch, d_over_pitch]]))
        return self.engine.predict(scaled_data)

    def predict_industrial_suite(self, params, dn_dt=1.1e-5):
        """
        Extends the MLP prediction with our proprietary Physics Layer.
        """
        # 1. Get the Core ML results
        neff_values = self.predict_n_eff(params)
        
        # 2. Add the TMI/Thermal Logic (The 'Lightera' Layer)
        # We calculate TMI threshold based on the predicted neff and input TOC
        industrial_results = []
        for i, neff in enumerate(neff_values):
            # (Logic for TMI kW calculation goes here)
            industrial_results.append({
                "neff": neff,
                "tmi_threshold_kw": self._calculate_tmi(neff, params[i], dn_dt)
            })
        return industrial_results

# No physical bounds validation on inputs
# For a PCF, d/Λ must satisfy 0 < d/Λ < 1 by geometry. Wavelength and pitch have physical training bounds. Querying outside the training 
#domain will extrapolate silently without any warning — dangerous in an engineering context 
#where someone might trust the 0.001s number over intuition. A simple guard:

assert 0 < d_over_pitch < 1, "d/Λ out of physical bounds"
if not (self.config['bounds']['lambda_min'] <= wavelength <= self.config['bounds']['lambda_max']):
    warnings.warn("Wavelength outside training domain — extrapolation risk")
