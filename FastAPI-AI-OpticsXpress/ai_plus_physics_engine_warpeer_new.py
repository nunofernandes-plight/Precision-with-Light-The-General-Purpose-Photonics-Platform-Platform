mport numpy as np
import joblib


class AIPlusPhysicsEngine:
    def __init__(self, model_path):
        """
        Loads the trained model and scalers from a joblib file.
        Expects the file to contain a 3-tuple: (model, scaler_x, scaler_y).
        """
        # FIX 1: Validate structure of the loaded object before unpacking
        loaded = joblib.load(model_path)
        if not (isinstance(loaded, (list, tuple)) and len(loaded) == 3):
            raise ValueError(
                f"Expected a 3-tuple (model, scaler_x, scaler_y) from '{model_path}', "
                f"but got {type(loaded)} of length {len(loaded) if hasattr(loaded, '__len__') else 'N/A'}."
            )
        self.model, self.scaler_x, self.scaler_y = loaded

        # Physical Constants for Yb-doped Silica fiber
        self.C_TMI = 1.4e-1          # Empirical scaling constant
        self.default_dn_dt = 1.1e-5  # Standard Silica thermo-optic coefficient (K^-1)

    def predict_with_tmi(
        self,
        wavelength: float,
        pitch: float,
        d_lambda: float,
        dn_dt: float = None,
        absorption_db_m: float = 0.35,
        neff_fsm: float = None,
    ):
        """
        Predicts optical properties and estimates the TMI threshold.

        Args:
            wavelength      : Operating wavelength (microns)
            pitch           : Hole-to-hole spacing Lambda (microns)
            d_lambda        : Hole diameter / pitch ratio (d/Lambda)
            dn_dt           : Thermo-optic coefficient (K^-1). Defaults to silica value.
            absorption_db_m : Cladding absorption in dB/m (e.g. Lightera's 0.35 dB/m)
            neff_fsm        : Effective index of the Fundamental Space-filling Mode.
                              If None, a placeholder offset of 0.005 is used (low accuracy).

        Returns:
            dict with n_eff, mode_area_um2, confinement_loss, v_parameter,
            is_single_mode, tmi_threshold_kw, toc_used.
        """
        if dn_dt is None:
            dn_dt = self.default_dn_dt

        # FIX 2: Guard against division by zero in TMI formula
        if dn_dt == 0:
            raise ValueError("dn_dt (thermo-optic coefficient) must not be zero.")
        if absorption_db_m == 0:
            raise ValueError("absorption_db_m must not be zero (would imply infinite TMI threshold).")

        # ------------------------------------------------------------------ #
        # 1. AI Inference: Get optical properties from the trained model
        # ------------------------------------------------------------------ #
        X_scaled = self.scaler_x.transform([[wavelength, pitch, d_lambda]])
        raw_preds = self.model.predict(X_scaled)

        # FIX 3: Ensure predictions are always 2D for inverse_transform
        # Some regressors return a 1D array for single-sample input.
        raw_preds = np.asarray(raw_preds).reshape(1, -1)

        unscaled_preds = self.scaler_y.inverse_transform(raw_preds)[0]

        # Mapping predicted outputs (order defined at training time)
        n_eff            = unscaled_preds[0]
        a_eff            = unscaled_preds[1]  # Effective Mode Area in µm²
        confinement_loss = unscaled_preds[2]  # FIX 4: Expose Confinement Loss instead of discarding it

        # ------------------------------------------------------------------ #
        # 2. Physics Layer: Simplified TMI Threshold Calculation
        #    Formula: P_tmi ~ C * (lambda² * A_eff) / (dn_dt * alpha)
        #    Ref: Smith & Smith, "Mode instability in high power fiber amplifiers"
        #    Note: C_TMI and the 1e-15 scale are empirical — units are not SI-consistent.
        # ------------------------------------------------------------------ #
        a_eff_m2 = a_eff * 1e-12                  # µm² → m²
        alpha_m  = absorption_db_m / 4.343         # dB/m → Np/m  (≈ ln10/10)
        lam_m    = wavelength * 1e-6               # µm  → m

        p_tmi_kw = (
            self.C_TMI
            * (lam_m ** 2 * a_eff_m2)
            / (dn_dt * alpha_m)
        ) * 1e15   # Empirical scale factor to bring result into kW range

        # ------------------------------------------------------------------ #
        # 3. Mode Stability Logic (V-parameter / Pi-Cutoff)
        #    V_eff = (2π·Λ/λ) · sqrt(n_eff² - n_FSM²)
        #    Single-mode condition: V_eff < π
        # ------------------------------------------------------------------ #
        if neff_fsm is None:
            # FIX 5: Clearly flag that the placeholder is in use
            import warnings
            warnings.warn(
                "neff_fsm not provided. Using a fixed offset of 0.005 from n_eff as a placeholder. "
                "This makes the V-parameter and single-mode result unreliable. "
                "Pass a physically computed neff_fsm for accurate results.",
                UserWarning,
                stacklevel=2,
            )
            neff_fsm = n_eff - 0.005

        # FIX 6: Guard against sqrt of negative number (would silently produce NaN)
        na2 = n_eff ** 2 - neff_fsm ** 2
        if na2 < 0:
            raise ValueError(
                f"n_eff ({n_eff:.6f}) must be greater than neff_fsm ({neff_fsm:.6f}). "
                "Check that the FSM index does not exceed the core effective index."
            )

        v_eff = (2 * np.pi * pitch / wavelength) * np.sqrt(na2)

        return {
            "n_eff":              float(n_eff),
            "mode_area_um2":      float(a_eff),
            "confinement_loss":   float(confinement_loss),   # Now returned
            "v_parameter":        float(v_eff),
            "is_single_mode":     bool(v_eff < np.pi),
            "tmi_threshold_kw":   round(float(p_tmi_kw), 2),
            "toc_used":           dn_dt,
        }
