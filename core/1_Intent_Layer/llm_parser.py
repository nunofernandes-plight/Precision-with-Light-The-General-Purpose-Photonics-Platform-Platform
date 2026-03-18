import os
import json
from .schemas import OpticalTargets, ComponentType, ManufacturingMethod

class IntentParser:
    """
    The 'Front Door': Converts natural language into structured Pydantic schemas.
    """
    def __init__(self, model_provider="gemini-3-flash"):
        self.model = model_provider

    def extract_intent(self, user_query: str) -> dict:
        """
        In production, this sends a prompt to the LLM.
        Example Prompt: 'Extract optical targets from: "I need a 1550nm fiber with high neff for Nanoscribe."'
        """
        # --- Logic for LLM Prompting ---
        # The LLM is instructed to return a JSON matching our OpticalTargets schema.
        
        # MOCK SUCCESSFUL EXTRACTION:
        extracted_json = {
            "wavelength_nm": 1550.0,
            "target_n_eff": 1.445,
            "component_type": "photonic_crystal_fiber",
            "method": "nanoscribe_2pp"
        }
        
        return extracted_json

    def create_request_packet(self, user_query: str):
        raw = self.extract_intent(user_query)
        
        # Validation happens here via Pydantic
        targets = OpticalTargets(
            wavelength_nm=raw["wavelength_nm"],
            target_n_eff=raw["target_n_eff"]
        )
        
        print(f"[Parser] Intent Extracted: λ={targets.wavelength_nm}nm, n_eff={targets.target_n_eff}")
        return targets, raw["method"]
