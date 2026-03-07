from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from .schemas import FiberInput, FiberOutput
from .engine_wrapper import PCFInferenceEngine

app = FastAPI(title="AI-Optics-Express API", version="1.0.0")

# Load our Physics-Informed model
engine = PCFInferenceEngine("models/global_brain_v1.pkl")

@app.post("/predict", response_model=FiberOutput)
async def predict_fiber_properties(data: FiberInput):
    try:
        # 1. Instant AI Prediction (< 1ms)
        results = engine.predict(data.wavelength, data.pitch, data.d_over_pitch)
        
        # 2. Physics-Based Post-Processing (Mortensen Theory)
        # V_eff calculation
        v_eff = (2 * 3.14159 * data.pitch / data.wavelength) * (results['neff_fm']**2 - results['neff_fsm']**2)**0.5
        
        return {
            "n_eff_real": results['neff_fm'],
            "dispersion": results['dispersion'],
            "mode_area": results['mode_area'],
            "v_parameter": v_eff,
            "is_single_mode": v_eff < 3.14159  # The Pi-Cutoff
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount the dashboard (Phase 3)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
