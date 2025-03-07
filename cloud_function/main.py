import functions_framework
import json
import logging
import traceback
from google.cloud import storage
from google.cloud import firestore
from google.cloud import aiplatform

from text_processing import extract_text_from_document
from chunking import chunk_text
from embeddings import generate_embeddings
from database import store_embeddings_in_vector_search, store_chunks_in_firestore
from config import SECTOR_INDEX_MAPPING

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clients
storage_client = storage.Client()
firestore_client = firestore.Client()


@functions_framework.http
def process_document(request):
    """
    Cloud Function entry point for document processing.

    Args:
        request (flask.Request): HTTP request object.

    Returns:
        The response text or any set of values that can be turned into a
        Response object using `make_response`.
    """
    # Set CORS headers for the preflight request
    if request.method == "OPTIONS":
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "3600",
        }
        return ("", 204, headers)

    # Set CORS headers for the main request
    headers = {"Access-Control-Allow-Origin": "*"}

    try:
        # Parse request JSON
        request_json = request.get_json(silent=True)

        if not request_json:
            return (
                json.dumps({"success": False, "error": "No JSON data provided"}),
                400,
                headers,
            )

        # Extract parameters
        document_id = request_json.get("document_id")
        blob_path = request_json.get("blob_path")
        sector = request_json.get("sector")
        processing_strategy = request_json.get("processing_strategy")
        processing_options = request_json.get("processing_options", {})
        embedding_task_type = request_json.get(
            "embedding_task_type", "RETRIEVAL_DOCUMENT"
        )

        # Validate required parameters
        if not all([document_id, blob_path, sector, processing_strategy]):
            return (
                json.dumps(
                    {
                        "success": False,
                        "error": "Missing required parameters. Required: document_id, blob_path, sector, processing_strategy",
                    }
                ),
                400,
                headers,
            )

        # Validate sector
        if sector not in SECTOR_INDEX_MAPPING:
            return (
                json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid sector: {sector}. Available sectors: {list(SECTOR_INDEX_MAPPING.keys())}",
                    }
                ),
                400,
                headers,
            )

        # Process the document
        logger.info(
            f"Processing document: {document_id}, blob_path: {blob_path}, sector: {sector}"
        )

        # 1. Download document from Cloud Storage
        bucket_name, object_name = parse_gcs_uri(blob_path)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(object_name)

        # Create a temporary file to store the document
        temp_file_path = f"/tmp/{document_id}"
        blob.download_to_filename(temp_file_path)
        logger.info(f"Downloaded document to {temp_file_path}")

        # 2. Extract text from document
        text = extract_text_from_document(temp_file_path)
        logger.info(f"Extracted {len(text)} characters of text")

        # 3. Chunk text based on strategy
        chunks = chunk_text(text, processing_strategy, processing_options)
        logger.info(
            f"Created {len(chunks)} chunks using {processing_strategy} strategy"
        )

        # 4. Generate embeddings for chunks with specified task type
        chunk_embeddings = generate_embeddings(chunks, embedding_task_type)
        logger.info(
            f"Generated embeddings for {len(chunk_embeddings)} chunks using task type: {embedding_task_type}"
        )

        # 5. Store embeddings in Vector Search
        vector_search_index = SECTOR_INDEX_MAPPING[sector]
        vector_ids = store_embeddings_in_vector_search(
            chunk_embeddings, vector_search_index
        )
        logger.info(f"Stored embeddings in Vector Search index: {vector_search_index}")

        # 6. Store chunks in Firestore
        firestore_refs = store_chunks_in_firestore(
            document_id=document_id,
            sector=sector,
            chunks=chunks,
            vector_ids=vector_ids,
            metadata={
                "original_blob_path": blob_path,
                "processing_strategy": processing_strategy,
                "processing_options": processing_options,
                "embedding_task_type": embedding_task_type,
            },
        )
        logger.info(f"Stored chunks in Firestore")

        # Return success response
        return (
            json.dumps(
                {
                    "success": True,
                    "document_id": document_id,
                    "sector": sector,
                    "chunk_count": len(chunks),
                    "vector_ids": vector_ids,
                    "embedding_task_type": embedding_task_type,
                }
            ),
            200,
            headers,
        )

    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        logger.error(traceback.format_exc())

        return (
            json.dumps({"success": False, "error": str(e)}),
            500,
            headers,
        )


def parse_gcs_uri(blob_path):
    """
    Parse a GCS blob path into bucket name and object name.

    Args:
        blob_path (str): The GCS blob path (can be with or without gs:// prefix)

    Returns:
        tuple: (bucket_name, object_name)
    """
    # If the path starts with gs://, remove it
    if blob_path.startswith("gs://"):
        blob_path = blob_path[5:]

    # Split the path into bucket and object
    parts = blob_path.split("/", 1)

    if len(parts) < 2:
        raise ValueError(f"Invalid GCS path: {blob_path}")

    bucket_name = parts[0]
    object_name = parts[1]

    return bucket_name, object_name
