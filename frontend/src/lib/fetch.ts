// If it is in fetch.ts, your import in the UI looks like this:
import { ingestPaper } from "@/lib/fetch";

// Define the TypeScript interface mirroring the Python Pydantic schema
export interface ResearchPaperPayload {
  title: string;
  authors: string[];
  doi?: string;
  topic_category: string;
  core_material: string;
  cladding_material: string;
  lattice_type?: string;
  hole_diameter_nm?: number;
  pitch_nm?: number;
  waveguide_width_nm?: number;
  waveguide_height_nm?: number;
  operating_wavelength_nm: number;
  suggested_solver: string;
}

// The function to call the FastAPI backend
export const ingestPaper = async (payload: ResearchPaperPayload) => {
  const API_URL = "http://localhost:8000/research/ingest-paper";

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error communicating with Scholar Bridge:", error);
    throw error;
  }
};
