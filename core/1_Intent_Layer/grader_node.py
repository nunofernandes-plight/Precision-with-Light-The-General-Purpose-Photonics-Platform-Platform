from .schemas import OpticalTargets, WaveguideGeometry, ComponentType
from .rag_config import DatabaseManager

class ReflexiveGrader:
    """
    The 'Cognitive Filter': Cross-references AI intent against MongoDB Ground Truth.
    Prevents physical hallucinations before they reach the Generative Engine.
    """
    def __init__(self):
        self.db_manager = DatabaseManager()

    def grade_waveguide_request(self, geometry: WaveguideGeometry, target_n_eff: float) -> dict:
        """
        Evaluates if the requested waveguide and target index are physically possible
        based on the retrieved Foundry Design Rules (DRC).
        """
        print(f"[Grader Node] Evaluating request for {geometry.cladding_material} cladding...")
        
        # 1. Retrieve the Ground Truth from MongoDB
        ground_truth = self.db_manager.fetch_constraints_by_material(geometry.cladding_material)
        
        if not ground_truth:
            return {
                "status": "fail",
                "reason": f"Material '{geometry.cladding_material}' not found in verified database.",
                "action": "rewrite_query"
            }

        # 2. Reflexive Grading (The Logic Gates)
        
        # Check A: Is the target refractive index mathematically possible?
        # n_eff cannot be higher than the core material (Silicon ~3.48) or lower than the cladding
        if target_n_eff < ground_truth["n_min"] or target_n_eff > 3.48:
            return {
                "status": "fail",
                "reason": f"Target n_eff ({target_n_eff}) violates physical limits for {geometry.cladding_material} cladding.",
                "action": "rewrite_query"
            }

        # Check B: Does the geometry violate Foundry Etch Limits?
        if geometry.etch_depth_nm > ground_truth["max_etch_depth_nm"]:
            return {
                "status": "fail",
                "reason": f"Requested etch depth ({geometry.etch_depth_nm}nm) exceeds foundry DRC maximum ({ground_truth['max_etch_depth_nm']}nm).",
                "action": "rewrite_query"
            }

        # 3. If it passes all checks
        print("[Grader Node] ✅ Request verified against physics constraints.")
        return {
            "status": "pass",
            "reason": "Geometry and targets are physically sound.",
            "action": "generate"
        }

  
