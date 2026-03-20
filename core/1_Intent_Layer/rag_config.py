import os
from pydantic import BaseModel, Field
from pymongo import MongoClient
from pymongo.collection import Collection

class VectorStoreConfig(BaseModel):
    """Configuration for MongoDB Atlas Vector Search."""
    # In production, these should be loaded from a .env file
    mongo_uri: str = Field(default_factory=lambda: os.getenv("MONGO_URI", "mongodb+srv://localhost:27017"))
    db_name: str = Field(default="precision_with_light_core")
    collection_name: str = Field(default="physics_constraints")
    index_name: str = Field(default="vector_index")
    embedding_dim: int = Field(default=1536) # Assuming OpenAI/standard embeddings

class PhysicsDocument(BaseModel):
    """The schema for the documents stored in MongoDB."""
    material_name: str
    component_type: str
    n_min: float
    n_max: float
    max_etch_depth_nm: float
    source_reference: str # e.g., "Foundry_DRC_v2.pdf"

class DatabaseManager:
    """Manages the Dual-State connection to MongoDB."""
    def __init__(self, config: VectorStoreConfig = VectorStoreConfig()):
        self.config = config
        self.client = MongoClient(self.config.mongo_uri)
        self.db = self.client[self.config.db_name]
        self.collection: Collection = self.db[self.config.collection_name]
        print(f"[RAG Config] Connected to MongoDB Atlas: {self.config.db_name}.{self.config.collection_name}")

    def fetch_constraints_by_material(self, material_name: str) -> dict:
        """
        Simulates a targeted lookup. In a full RAG pipeline, 
        this would execute a vector search ($vectorSearch) using the user's embedded query.
        """
        # Mocking a database hit for the sake of architecture
        mock_db = {
            "SiO2": {"n_min": 1.440, "n_max": 1.448, "max_etch_depth_nm": 3000.0},
            "Silicon": {"n_min": 3.450, "n_max": 3.480, "max_etch_depth_nm": 220.0} # Standard SOI
        }
        return mock_db.get(material_name, None)

  
