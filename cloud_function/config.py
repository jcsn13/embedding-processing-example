"""
Copyright 2025 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
Configuration settings for the document processing system.
"""

import os
import json

# Get environment variables
PROJECT_ID = os.environ.get("PROJECT_ID", "your-project")
REGION = os.environ.get("REGION", "us-central1")
BUCKET_NAME = os.environ.get("BUCKET_NAME", "your-document-bucket")

# Get sectors from environment variable
SECTORS_ENV = os.environ.get(
    "SECTORS", "accounting hr legal engineering sales marketing"
)
# Handle both comma-separated and space-separated formats
if "," in SECTORS_ENV:
    SECTORS = [sector.strip() for sector in SECTORS_ENV.split(",")]
else:
    SECTORS = [sector.strip() for sector in SECTORS_ENV.split()]

# Mapping of sectors to Vector Search indexes
SECTOR_INDEX_MAPPING = {
    sector: f"projects/{PROJECT_ID}/locations/{REGION}/indexes/{sector}-index"
    for sector in SECTORS
}

# Default processing options for each strategy
DEFAULT_PROCESSING_OPTIONS = {
    "fixed_size": {
        "chunk_size": int(os.environ.get("FIXED_SIZE_CHUNK_SIZE", "512")),
    },
    "semantic": {
        "min_chunk_size": int(os.environ.get("SEMANTIC_MIN_CHUNK_SIZE", "100")),
        "max_chunk_size": int(os.environ.get("SEMANTIC_MAX_CHUNK_SIZE", "1000")),
    },
    "sliding_window": {
        "chunk_size": int(os.environ.get("SLIDING_WINDOW_CHUNK_SIZE", "512")),
        "overlap": int(os.environ.get("SLIDING_WINDOW_OVERLAP", "128")),
    },
    "hierarchical": {
        "levels": json.loads(
            os.environ.get("HIERARCHICAL_LEVELS", '["document", "paragraph"]')
        ),
    },
}

# Embedding model settings
EMBEDDING_MODEL = {
    "model_name": os.environ.get(
        "EMBEDDING_MODEL_NAME", "text-multilingual-embedding-002"
    ),
    "dimensions": int(os.environ.get("EMBEDDING_DIMENSIONS", "768")),
}

# Firestore collection structure
FIRESTORE_STRUCTURE = {
    "sectors_collection": os.environ.get("SECTORS_COLLECTION", "sectors"),
    "documents_collection": os.environ.get("DOCUMENTS_COLLECTION", "documents"),
    "chunks_collection": os.environ.get("CHUNKS_COLLECTION", "chunks"),
}

# Cloud Storage settings
STORAGE_SETTINGS = {
    "temp_directory": os.environ.get("TEMP_DIRECTORY", "/tmp"),
    "bucket_name": BUCKET_NAME,
}
