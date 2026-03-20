from .schemas import WaveguideGeometry
from .rag_config import DatabaseManager

class QueryRewriter:
    """
    The 'Self-Correction Loop'.
    If the Grader Node rejects a request, this LLM-agent adjusts the user's 
    intent to find the nearest physically valid design parameters.
    """
    def __init__(self):
        self.db_manager = DatabaseManager()

    def autocorrect_waveguide(self, geometry: WaveguideGeometry, target_n_eff: float, failure_reason: str) -> dict:
        """
        Takes the rejected geometry and the Grader's rejection reason,
        and calculates the nearest valid physical parameters.
        """
        print(f"[Rewriter Node] Triggered. Reason: {failure_reason}")
        ground_truth = self.db_manager.fetch_constraints_by_material(geometry.cladding_material)
        
        # Create copies of the original requests to modify
        corrected_geometry = geometry.copy()
        corrected_n_eff = target_n_eff

        # 1. Fix Etch Depth Violations
        if "etch depth" in failure_reason.lower():
            max_allowed = ground_truth["max_etch_depth_nm"]
            print(f"[Rewriter Node] Auto-correcting etch depth from {geometry.etch_depth_nm}nm to {max_allowed}nm.")
            corrected_geometry.etch_depth_nm = max_allowed

        # 2. Fix Refractive Index Violations
        if "n_eff" in failure_reason.lower():
            min_n = ground_truth["n_min"]
            if target_n_eff < min_n:
                print(f"[Rewriter Node] Auto-correcting n_eff from {target_n_eff} to {min_n}.")
                corrected_n_eff = min_n
            elif target_n_eff > 3.48: # Silicon core max
                print(f"[Rewriter Node] Auto-correcting n_eff from {target_n_eff} to 3.45.")
                corrected_n_eff = 3.45

        return {
            "corrected_geometry": corrected_geometry,
            "corrected_n_eff": corrected_n_eff,
            "message": f"Parameters auto-corrected to meet Foundry DRC for {geometry.cladding_material}."
        }


