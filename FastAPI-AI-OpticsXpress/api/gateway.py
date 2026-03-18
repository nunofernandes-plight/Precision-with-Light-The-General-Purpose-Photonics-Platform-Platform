from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

# Importing our modular layers
from ..1_intent_layer.llm_parser import IntentParser
from ..2_generative_engine.models.pcf_gan import PCFGenerativeService
from ..4_fabrication_export.export_nanoscribe import NanoscribeExporter
from ..4_fabrication_export.export_gdsii import GDSIIExporter

app = FastAPI(title="Precision with Light: General Purpose Photonics Platform")

# --- Persistent Service Instances ---
parser = IntentParser()
# Point to your audited PCF weights
pcf_engine = PCFGenerativeService(model_path="models/final_pcf_gan.pt") 
nanoscribe = NanoscribeExporter()
foundry = GDSIIExporter()

class UserPrompt(BaseModel):
    text: str # e.g., "Design a fiber for 1550nm for 3D printing"

@app.post("/generate-design")
async def generate_design(request: UserPrompt):
    """
    The Zero-Touch Pipeline:
    Natural Language -> Structured Intent -> AI Synthesis -> Fab Export
    """
    try:
        # 1. Intent Layer: Extract parameters from text
        targets, method = parser.create_request_packet(request.text)
        
        # 2. Generative Layer: AI Synthesizes the geometry
        # Currently defaults to PCF; future logic will route based on ComponentType
        geometry = pcf_engine.synthesize(targets)
        
        # 3. Fabrication Layer: Export based on requested method
        export_path = ""
        if method == "nanoscribe_2pp":
            export_path = nanoscribe.create_pcf_mesh(geometry, filename=f"exports/design_{targets.wavelength_nm}.stl")
        elif method == "silicon_foundry":
            export_path = foundry.generate_layout(geometry, output_path=f"exports/mask_{targets.wavelength_nm}.gds")
        
        return {
            "status": "success",
            "design": geometry.dict(),
            "download_link": export_path,
            "message": f"Design optimized for {method}."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
