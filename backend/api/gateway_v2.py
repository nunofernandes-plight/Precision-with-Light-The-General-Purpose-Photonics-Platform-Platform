import sys
import os
import importlib

# 1. Dynamically find the backend root directory
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

# 2. Bypass the "No numbers in imports" rule using importlib
intent_module = importlib.import_module("1_intent_layer.schemas")

# 3. Pull your Pydantic class into the gateway
ResearchPaperIngestion = intent_module.ResearchPaperIngestion

from fastapi import APIRouter
# Import your schema (adjust the path based on your exact folder structure)
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from 1_intent_layer.schemas import ResearchPaperIngestion

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

# --- 1. Intent & RAG Layer ---
from ..1_intent_layer.grader_node import ReflexiveGrader
from ..1_intent_layer.query_rewriter import QueryRewriter
from ..1_intent_layer.schemas import WaveguideGeometry

# --- 2. Generative Engine ---
from ..2_generative_engine.models.waveguide_regressor import WaveguidePredictorService

# --- 3. Trust Layer (Simulation) ---
from ..3_simulation_bridge.simulation_bridge import SimulationBridge

# --- 4. Fabrication Layer ---
from ..4_fabrication_export.export_gdsii import GDSIIExporter

app = FastAPI(title="Precision with Light: Enterprise Foundry Platform", version="2.0")

from fastapi.middleware.cors import CORSMiddleware

# ... (your app initialization)
app = FastAPI(title="Precision with Light: Enterprise Foundry Platform", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with your specific frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router_research = APIRouter(prefix="/research", tags=["Scholar Bridge"])

@router_research.post("/ingest-paper")
async def ingest_research_paper(paper: ResearchPaperIngestion):
    pipeline_logs = [f"📖 Ingesting paper: {paper.title}"]

    core = paper.core_material
    cladding = paper.cladding_material
    pipeline_logs.append(f"🧪 Material System: {core} Core with {cladding} Cladding")

    if paper.topic_category.lower() == "pcf":
        geometry_summary = {
            "type": "photonic_crystal_fiber",
            "lattice": paper.lattice_type or "hexagonal",
            "pitch_nm": paper.pitch_nm,
            "hole_diameter_nm": paper.hole_diameter_nm
        }
    else:
        geometry_summary = {
            "type": "waveguide",
            "width_nm": paper.waveguide_width_nm,
            "height_nm": paper.waveguide_height_nm
        }

    return {
        "status": "success",
        "paper_metadata": {"title": paper.title, "category": paper.topic_category},
        "reconstructed_geometry": geometry_summary,
        "suggested_simulation": {"engine": paper.suggested_solver, "wavelength_nm": paper.operating_wavelength_nm},
        "pipeline_logs": pipeline_logs
    }

# Initialize Services
grader = ReflexiveGrader()
rewriter = QueryRewriter()
silicon_engine = WaveguidePredictorService()
foundry = GDSIIExporter()

class UserPrompt(BaseModel):
    wavelength_nm: float = 1550.0
    cladding: str = "SiO2"
    target_n_eff: float
    requested_etch_depth_nm: float
    solver_choice: str = "lumerical" # Allows user to pick their solver!

@app.post("/generate-and-verify")
async def generate_and_verify(request: UserPrompt):
    """
    The Full Enterprise Pipeline: 
    Grade (RAG) -> Rewrite -> Predict (AI) -> Verify (Physics) -> Export (GDSII)
    """
    try:
        # 1. Base Geometry Assumption (From an LLM parser upstream)
        geometry = WaveguideGeometry(
            width_nm=500.0, 
            height_nm=220.0, 
            etch_depth_nm=request.requested_etch_depth_nm,
            cladding_material=request.cladding
        )
        current_n_eff = request.target_n_eff
        pipeline_logs = []

        # 2. DSR-CRAG: Reflexive Grading against MongoDB Foundry Limits
        grade_result = grader.grade_waveguide_request(geometry, current_n_eff)

        if grade_result["status"] == "fail":
            pipeline_logs.append(f"❌ Violation Detected: {grade_result['reason']}")
            # Self-Correction
            correction = rewriter.autocorrect_waveguide(geometry, current_n_eff, grade_result['reason'])
            geometry = correction["corrected_geometry"]
            current_n_eff = correction["corrected_n_eff"]
            pipeline_logs.append(f"✅ Auto-Corrected: {correction['message']}")
        else:
            pipeline_logs.append("✅ DRC Check Passed: No physics violations detected.")

        # 3. Generative AI Prediction ---
        ai_targets = silicon_engine.predict_performance(geometry, request.wavelength_nm)
        pipeline_logs.append(f"🤖 AI Prediction: n_eff = {ai_targets.target_n_eff:.4f}")

        # 4. The Trust Layer: Dynamic Solver Routing ---
        # Instead of hardcoding "lumerical", we use the user's input from the request
        bridge = SimulationBridge(solver_type=request.solver_choice) 
        
        # This will now trigger _run_comsol_mesh if request.solver_choice == "comsol"
        verification = bridge.verify_waveguide(geometry, request.wavelength_nm)

        # Calculate the Truth Metric (Fidelity)
        fidelity = bridge.calculate_fidelity(
            ai_prediction=ai_targets.target_n_eff, 
            solver_truth=verification["verified_n_eff"]
        )

        # 5. Final Unified Response ---
        return {
            "status": "success",
            "pipeline_diagnostics": pipeline_logs,
            "final_design": geometry.dict(),
            "ai_prediction": ai_targets.dict(),
            "physics_verification": {
                "solver_engine": verification["solver_used"], # Will show 'COMSOL' or 'Lumerical'
                "verified_n_eff": verification["verified_n_eff"],
                "fidelity_score": f"{fidelity * 100:.2f}%",
                "mesh_complexity": verification.get("mesh_elements", "N/A")
            },
            "fabrication_export": gds_filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.include_router(router_research)





