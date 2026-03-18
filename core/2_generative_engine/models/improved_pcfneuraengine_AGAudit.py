import warnings
import joblib
import numpy as np


class PCFModel:
    """
    Inference wrapper for a pre-trained MLP regressor that predicts the
    effective refractive index (n_eff) of a Photonic Crystal Fiber (PCF).

    Physical input parameters:
        - wavelength   (λ):   light wavelength in µm
        - pitch        (Λ):   inter-hole center-to-center distance in µm
        - d_over_pitch (d/Λ): air-hole diameter / pitch (dimensionless, must be in (0, 1))
    """

    # Default physical training bounds — override via constructor if needed.
    DEFAULT_BOUNDS = {
        "lambda_min": 0.5,   # µm  — adjust to your training data range
        "lambda_max": 2.0,   # µm
        "pitch_min":  1.0,   # µm
        "pitch_max":  5.0,   # µm
    }

    def __init__(
        self,
        model_path: str = "models/final_mlp.pkl",
        scaler_path: str = "models/scaler.pkl",
        bounds: dict = None,
    ):
        """
        Load the serialised MLP model and its associated feature scaler.

        Args:
            model_path:  Path to the joblib-serialised sklearn regressor.
            scaler_path: Path to the joblib-serialised StandardScaler.
            bounds:      Optional dict overriding DEFAULT_BOUNDS. Keys:
                         lambda_min, lambda_max, pitch_min, pitch_max.
        """
        self.engine = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        self.bounds = {**self.DEFAULT_BOUNDS, **(bounds or {})}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _validate_inputs(self, wavelength: float, pitch: float, d_over_pitch: float) -> None:
        """
        Raise or warn when inputs violate physical or training-domain constraints.

        Physical hard constraint (geometry):
            0 < d/Λ < 1   — air holes cannot be absent or overlap.

        Soft training-domain constraints (extrapolation risk):
            wavelength and pitch should lie within the bounds seen during training.
        """
        # --- Hard geometric constraint ---
        if not (0 < d_over_pitch < 1):
            raise ValueError(
                f"d/Λ = {d_over_pitch:.4f} is outside the physical range (0, 1). "
                "Air-hole diameter cannot equal or exceed the pitch."
            )

        # --- Soft training-domain constraints (warn, don't crash) ---
        b = self.bounds
        if not (b["lambda_min"] <= wavelength <= b["lambda_max"]):
            warnings.warn(
                f"Wavelength {wavelength} µm is outside the training range "
                f"[{b['lambda_min']}, {b['lambda_max']}] µm — extrapolation risk.",
                UserWarning,
                stacklevel=3,
            )

        if not (b["pitch_min"] <= pitch <= b["pitch_max"]):
            warnings.warn(
                f"Pitch {pitch} µm is outside the training range "
                f"[{b['pitch_min']}, {b['pitch_max']}] µm — extrapolation risk.",
                UserWarning,
                stacklevel=3,
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def predict_n_eff(self, params) -> np.ndarray:
        """
        Predict the effective refractive index (n_eff) for one or more parameter sets.

        Args:
            params: array-like of shape (n_samples, 3) or (3,) for a single sample.
                    Column order: [wavelength (µm), pitch (µm), d/Λ (dimensionless)]

        Returns:
            np.ndarray of shape (n_samples,) containing the predicted n_eff values.

        Raises:
            ValueError: if any d/Λ value is outside (0, 1).
        """
        data = np.atleast_2d(params)  # ensure shape is (n_samples, 3)

        if data.shape[1] != 3:
            raise ValueError(
                f"Expected 3 features [wavelength, pitch, d/Λ], got {data.shape[1]}."
            )

        # Validate every row before committing to inference
        for i, row in enumerate(data):
            wavelength, pitch, d_over_pitch = row
            try:
                self._validate_inputs(wavelength, pitch, d_over_pitch)
            except ValueError as exc:
                raise ValueError(f"Sample index {i}: {exc}") from exc

        scaled_data = self.scaler.transform(data)
        return self.engine.predict(scaled_data)
