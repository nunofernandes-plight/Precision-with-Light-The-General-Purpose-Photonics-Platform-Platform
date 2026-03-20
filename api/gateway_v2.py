from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

# Importing the Modular Layers
from ..1_intent_layer.llm_parser import IntentParser
from ..1_intent_layer.grader_node import ReflexiveGrader
from ..1_intent_layer.query_rewriter import QueryRewriter
from ..2_generative_engine.models.waveguide_regressor import WaveguidePredictorService
from ..4_fabrication_export.export_gdsii import GDSIIExporter
from ..1_intent_layer.schemas import WaveguideGeometry

app = FastAPI(title="Precision with Light: DSR-CRAG Integrated Platform")

# --- Persistent Service Instances ---
parser = IntentParser()
grader = ReflexiveGrader()
rewriter = QueryRewriter()
silicon_engine = WaveguidePredictorService()
foundry = GDSIIExporter()

class UserPrompt(BaseModel):
    text: str 
    cladding: str = "SiO2"
    target_n_eff: float
    requested_etch_depth_nm: float

@app.post("/generate-silicon-component")
async def generate_silicon_component(request: UserPrompt):
    """
    The Full Pipeline: Parse -> Reflexive Grade -> Rewrite (Optional) -> Predict -> Export
    """
    try:
        # 1. Parse (Mocking the LLM parsing the text into a schema)
        geometry = WaveguideGeometry(
            width_nm=500.0, 
            height_nm=220.0, 
            etch_depth_nm=request.requested_etch_depth_nm,
            cladding_material=request.cladding
        )
        current_n_eff = request.target_n_eff
        pipeline_messages = []

        # 2. Reflexive Grading (The DSR-CRAG Gatekeeper)
        grade_result = grader.grade_waveguide_request(geometry, current_n_eff)

        # 3. The Self-Correction Loop
        if grade_result["status"] == "fail":
            pipeline_messages.append(f"Constraint Violation: {grade_result['reason']}")
            
            # Route to Rewriter
            correction = rewriter.autocorrect_waveguide(geometry, current_n_eff, grade_result['reason'])
            
            # Apply corrections
            geometry = correction["corrected_geometry"]
            current_n_eff = correction["corrected_n_eff"]
            pipeline_messages.append(correction["message"])

        # 4. Generative Engine (Forward Prediction on the Verified Data)
        predicted_targets = silicon_engine.predict_performance(geometry)

        # 5. Fabrication Export
        gds_path = foundry.draw_waveguide(geometry)
        foundry.finalize(output_path="exports/verified_waveguide.gds")

        return {
            "status": "success",
            "final_geometry": geometry.dict(),
            "predicted_performance": predicted_targets.dict(),
            "pipeline_logs": pipeline_messages,
            "download_link": "exports/verified_waveguide.gds"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
