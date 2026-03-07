# Project Structure for pcf-api-demo

This setup allows an engineer or industry partner to interact with a "Software-Defined" fiber file in real-time. 
Instead of waiting for a batch of simulations to finish, they can adjust sliders for pitch or wavelength 
and see the optical response instantly.
```
/api
├── main.py            # FastAPI Application
├── schemas.py         # Data validation (Pydantic)
├── engine_wrapper.py  # Model loading and inference logic
├── /static            # HTML/JS for the Slider Dashboard
└── requirements.txt
```

## 1. The Data Schema (schemas.py)

We use Pydantic to enforce physical constraints. 
This ensures that the AI never attempts to predict results for unphysical geometries (e.g.,<img width="74" height="30" alt="image" src="https://github.com/user-attachments/assets/29529b72-95f0-46d4-9122-680662608006" />)


```
from pydantic import BaseModel, Field

class FiberInput(BaseModel):
    wavelength: float = Field(..., gt=0.3, lt=3.0, description="Wavelength in microns")
    pitch: float = Field(..., gt=0.5, lt=10.0, description="Hole pitch in microns")
    d_over_pitch: float = Field(..., gt=0.1, lt=0.9, description="d/Lambda ratio")

class FiberOutput(BaseModel):
    n_eff_real: float
    dispersion: float
    mode_area: float
    v_parameter: float
    is_single_mode: bool
```

## 2. The API Logic (main.py)
This script handles the "Real-Time" inference.
Notice the inclusion of the Mortensen <img width="15" height="19" alt="image" src="https://github.com/user-attachments/assets/ff5a6eee-0229-4053-bc03-8aff56938df0" />-cutoff as a logic gate for the is_single_mode flag.

```
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
```

## 3. The "Investor Moment": The Slider Dashboard

Inside your /static folder, you would have a simple index.html with JavaScript. 
This creates the visual "Wow" factor. When an investor moves a slider, the browser sends
a POST request to our FastAPI backend and updates a chart (using Chart.js or Plotly) in milliseconds.

## The Pitch Narrative for the Demo:

"Look at the screen. Typically, changing this fiber's pitch by 50nm would require a complete re-mesh and a 10-minute wait in a solver. 
With our Software-Defined API, the update is instantaneous. 
We can now optimize entire laser systems in the time it used to take to simulate a single fiber."

## Why this FastAPI setup is "Takeoff" Ready:

1. Automatic Documentation: FastAPI automatically generates a Swagger UI at /docs. You can send this link to a potential industrial partner, and their software team can test your model immediately without reading a single line of your training code.
2. Scalability: This API can be deployed in a Docker container on AWS or Azure. You can handle thousands of design requests per second, making it viable for a Cloud-Based Design Foundry.
3. Digital Twin Integration: A fiber draw-tower controller can call this API in a loop. As the glass is being pulled, the API calculates the optical specs in real-time based on live sensor data (pitch/diameter). If the <img width="37" height="30" alt="image" src="https://github.com/user-attachments/assets/b9349ede-1788-4967-9733-f8546d8b6091" />
 approaches the <img width="15" height="19" alt="image" src="https://github.com/user-attachments/assets/022684f9-87f6-4a03-a381-951d09ea49d6" />-boundary, the system can auto-adjust the draw speed.



