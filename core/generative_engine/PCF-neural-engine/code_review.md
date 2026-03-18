# Code Review: `AIPlusPhysicsEngine`

## What This Code Does (Conceptual Overview)

This class is a **hybrid AI + Physics inference engine** for photonic crystal fiber (PCF) design. It combines:

1. A **pre-trained ML model** (e.g. PINN or scikit-learn regressor) to predict optical properties from fiber geometry.
2. A **physics layer** that applies classical fiber optics equations on top of the predictions.

---

## Section-by-Section Breakdown

### `__init__`
Loads three objects from a single `joblib` file: the model, an input scaler, and an output scaler.

> [!IMPORTANT]
> **Runtime Risk**: `joblib.load` is expected to unpack into exactly 3 values.
> If the saved file has a different structure (e.g., a dict, or only 2 items), this line will raise a `ValueError` with no helpful message.
> **Recommendation**: wrap it in a try/except and validate the types.

```python
# Safer version
loaded = joblib.load(model_path)
if not (isinstance(loaded, (list, tuple)) and len(loaded) == 3):
    raise ValueError(f"Expected (model, scaler_x, scaler_y), got: {type(loaded)}")
self.model, self.scaler_x, self.scaler_y = loaded
```

---

### Step 1 — AI Inference

```python
X_scaled = self.scaler_x.transform([[wavelength, pitch, d_lambda]])
preds = self.model.predict(X_scaled)
unscaled_preds = self.scaler_y.inverse_transform(preds)[0]
```

**Correct assumption**: sklearn scalers and `predict()` expect 2D input `(1, 3)`. ✅

> [!WARNING]
> **Runtime Risk**: If `self.model.predict()` returns a **1D array** (some regressors do this for single-sample input), `scaler_y.inverse_transform()` will raise a `ValueError` because it expects a 2D array `(n_samples, n_features)`.
> **Fix**: ensure output is 2D:
> ```python
> preds = self.model.predict(X_scaled).reshape(1, -1)
> ```

> [!NOTE]
> The comment says the model predicts **3 outputs** (neff, Aeff, Confinement Loss), but only indices `[0]` and `[1]` are consumed. Index `[2]` (Confinement Loss) is silently ignored. This is not a bug, but it is dead output.

---

### Step 2 — TMI Threshold Physics

```python
a_eff_m2 = a_eff * 1e-12          # μm² → m²  ✅
alpha_m  = absorption_db_m / 4.343  # dB/m → Np/m ✅ (ln10/10 ≈ 0.2303, so 1/4.343)

p_tmi_kw = C_TMI * (wavelength * 1e-6)**2 * a_eff_m2 / (dn_dt * alpha_m)
p_tmi_kw *= 1e15
```

**Unit conversions are physically correct.**

> [!CAUTION]
> **Dimensional analysis fails**: The formula produces units of `m⁴ · K`, not Watts or kW. The calculation is empirical — `C_TMI = 1.4e-1` and the `1e15` scale factor together paper over the unit mismatch. This is acceptable as a fast approximation **only if** the model is calibrated against real TMI measurements. It should **not** be used as an ab-initio result.

> [!WARNING]
> **Runtime Risk — Division by Zero**: If `absorption_db_m = 0` or `dn_dt = 0` is passed, `alpha_m` or `dn_dt` will be zero and the division will raise `ZeroDivisionError`. No guard is present.
> **Fix**:
> ```python
> if dn_dt == 0 or absorption_db_m == 0:
>     raise ValueError("dn_dt and absorption_db_m must be non-zero.")
> ```

---

### Step 3 — V-Parameter and Single-Mode Check

```python
neff_fsm = n_eff - 0.005  # ← Hardcoded placeholder
v_eff = (2 * np.pi * pitch / wavelength) * np.sqrt(n_eff**2 - neff_fsm**2)
is_single_mode = v_eff < np.pi
```

**Conceptual explanation**: The V-parameter (or normalised frequency) for a PCF is:

```
V_eff = (2π · Λ / λ) · NA_eff
where NA_eff = sqrt(n_eff² - n_FSM²)
```

The FSM (Fundamental Space-filling Mode) index `n_FSM` represents the effective cladding index. `V_eff < π` is the **single-mode cutoff** (analogous to `V < 2.405` for step-index fibers).

> [!IMPORTANT]
> **Physical Issue**: `neff_fsm = n_eff - 0.005` is a **placeholder delta**, not a real FSM index. The FSM index must be computed from the cladding geometry (air-fill fraction, pitch). Using a fixed offset makes the V-parameter and the single-mode condition unreliable for any fiber where the real Δn_eff ≠ 0.005.
> **Recommendation**: Replace with an FSM lookup table or a secondary model head as noted in the comment.

> [!NOTE]
> **Potential NaN Risk**: Since `neff_fsm = n_eff - 0.005`, the argument to `sqrt` simplifies to `≈ 0.01·n_eff`, which is always positive for real fibers. No NaN risk **given the current placeholder**. However, if `neff_fsm` is later set from a real model and exceeds `n_eff`, `sqrt` will return `nan` silently.
> **Fix**: Add an assertion:
> ```python
> assert n_eff > neff_fsm, "n_eff must be greater than neff_fsm (cladding index)"
> ```

---

## Summary Table

| Issue | Type | Severity |
|---|---|---|
| `joblib.load` unpack assumes 3-tuple structure | Runtime Error | 🔴 High |
| `model.predict()` may return 1D array → `inverse_transform` fails | Runtime Error | 🔴 High |
| Division by zero if `absorption_db_m=0` or `dn_dt=0` | Runtime Error | 🟠 Medium |
| `neff_fsm` is a fixed placeholder, not a physical value | Physical/Conceptual | 🟠 Medium |
| TMI formula is empirical, not dimensionally consistent | Conceptual | 🟡 Low (by design) |
| Confinement Loss output (index 2) is predicted but never used | Unused Output | 🟡 Low |
| No guard against `n_eff < neff_fsm` in future FSM updates | Latent Bug | 🟡 Low |
