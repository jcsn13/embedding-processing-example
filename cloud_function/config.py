"""
Configuration settings for the document processing system.
"""

# Mapping of sectors to Vector Search indexes
SECTOR_INDEX_MAPPING = {
    "accounting": "projects/your-project/locations/us-central1/indexes/accounting-index",
    "hr": "projects/your-project/locations/us-central1/indexes/hr-index",
    "legal": "projects/your-project/locations/us-central1/indexes/legal-index",
    "engineering": "projects/your-project/locations/us-central1/indexes/engineering-index",
    "sales": "projects/your-project/locations/us-central1/indexes/sales-index",
    "marketing": "projects/your-project/locations/us-central1/indexes/marketing-index",
}

# Default processing options for each strategy
DEFAULT_PROCESSING_OPTIONS = {
    "fixed_size": {
        "chunk_size": 512,
    },
    "semantic": {
        "min_chunk_size": 100,
        "max_chunk_size": 1000,
    },
    "sliding_window": {
        "chunk_size": 512,
        "overlap": 128,
    },
    "hierarchical": {
        "levels": ["document", "paragraph"],
    },
}

# Embedding model settings
EMBEDDING_MODEL = {
    "endpoint_id": "text-embedding-endpoint",
    "location": "us-central1",
    "dimensions": 768,  # Adjust based on the model used
}

# Firestore collection structure
FIRESTORE_STRUCTURE = {
    "sectors_collection": "sectors",
    "documents_collection": "documents",
    "chunks_collection": "chunks",
}

# Cloud Storage settings
STORAGE_SETTINGS = {
    "temp_directory": "/tmp",
}
