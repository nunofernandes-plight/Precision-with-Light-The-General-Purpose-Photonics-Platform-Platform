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
        scaled_data = self.scaler.transform(data)
        return self.engine.predict(scaled_data)
