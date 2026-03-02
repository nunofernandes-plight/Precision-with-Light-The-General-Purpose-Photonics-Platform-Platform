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
        
# No physical bounds validation on inputs
# For a PCF, d/Λ must satisfy 0 < d/Λ < 1 by geometry. Wavelength and pitch have physical training bounds. Querying outside the training 
#domain will extrapolate silently without any warning — dangerous in an engineering context 
#where someone might trust the 0.001s number over intuition. A simple guard:

assert 0 < d_over_pitch < 1, "d/Λ out of physical bounds"
if not (self.config['bounds']['lambda_min'] <= wavelength <= self.config['bounds']['lambda_max']):
    warnings.warn("Wavelength outside training domain — extrapolation risk")
