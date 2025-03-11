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
from config import SECTOR_INDEX_MAPPING, BUCKET_NAME

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
        logger.info(f"Using configured bucket: {bucket_name} for object: {object_name}")

        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(object_name)

        # Create a temporary file to store the document
        temp_file_path = f"/tmp/{document_id}"
        try:
            blob.download_to_filename(temp_file_path)
            logger.info(f"Downloaded document to {temp_file_path}")
        except Exception as download_error:
            error_message = str(download_error)
            logger.error(f"Error downloading file: {error_message}")

            # Provide more helpful error message
            if "403" in error_message:
                return (
                    json.dumps(
                        {
                            "success": False,
                            "error": f"Access denied to bucket '{bucket_name}'. Please check project billing status and service account permissions.",
                            "details": error_message,
                        }
                    ),
                    403,
                    headers,
                )
            elif "404" in error_message or "Not Found" in error_message:
                return (
                    json.dumps(
                        {
                            "success": False,
                            "error": f"File not found: '{object_name}' in bucket '{bucket_name}'. Please check that the file exists at this path.",
                            "details": error_message,
                            "suggestion": "If you uploaded the file to a different path, make sure the blob_path parameter matches the actual file location.",
                        }
                    ),
                    404,
                    headers,
                )
            else:
                # Re-raise for general error handling
                raise

        # 2. Extract text from document
        try:
            text = extract_text_from_document(temp_file_path)
            logger.info(f"Extracted {len(text)} characters of text")
        except Exception as text_error:
            error_message = str(text_error)
            logger.error(f"Error extracting text from document: {error_message}")
            return (
                json.dumps(
                    {
                        "success": False,
                        "error": "Failed to extract text from the document",
                        "details": error_message,
                        "suggestion": "The file may be corrupted, password-protected, or in an unsupported format.",
                    }
                ),
                400,
                headers,
            )

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
        error_message = str(e)
        logger.error(f"Error processing document: {error_message}")
        logger.error(traceback.format_exc())

        # Determine if this is a known error type
        if (
            "billing account" in error_message.lower()
            and "disabled" in error_message.lower()
        ):
            status_code = 403
            error_response = {
                "success": False,
                "error": "The Google Cloud project's billing account is disabled. Please enable billing for the project to access storage resources.",
                "details": error_message,
            }
        elif "storage.googleapis.com" in error_message and "403" in error_message:
            status_code = 403
            error_response = {
                "success": False,
                "error": f"Access denied to Google Cloud Storage bucket '{BUCKET_NAME}'. Please check project billing status and service account permissions.",
                "details": error_message,
            }
        elif "404" in error_message or "Not Found" in error_message:
            status_code = 404
            error_response = {
                "success": False,
                "error": "File not found in storage bucket. Please check that the file exists at the specified path.",
                "details": error_message,
                "suggestion": "If you uploaded the file to a different path, make sure the blob_path parameter matches the actual file location.",
            }
        else:
            status_code = 500
            error_response = {
                "success": False,
                "error": "An error occurred while processing the document",
                "details": error_message,
            }

        return (
            json.dumps(error_response),
            status_code,
            headers,
        )


def parse_gcs_uri(blob_path):
    """
    Parse a GCS blob path to extract the object name while preserving directory structure.
    Always uses the configured bucket name from environment variables.

    Args:
        blob_path (str): The GCS blob path (can be with or without gs:// prefix)

    Returns:
        tuple: (bucket_name, object_name) where bucket_name is always the configured BUCKET_NAME
    """
    # If the path starts with gs://, remove it
    if blob_path.startswith("gs://"):
        blob_path = blob_path[5:]

    # Extract the object name while preserving directory structure
    if "/" in blob_path:
        # First, split to separate bucket name from the rest
        parts = blob_path.split("/", 1)

        # Check if the first part is a sector name (like "accounting")
        # If it is, we want to preserve it as part of the object path
        first_part = parts[0]
        rest_of_path = parts[1] if len(parts) > 1 else ""

        # If the first part is a sector name and there's more to the path,
        # include it in the object name to preserve the directory structure
        if first_part in SECTOR_INDEX_MAPPING.keys():
            object_name = f"{first_part}/{rest_of_path}"
        else:
            # If it's not a recognized sector, just use the rest of the path
            object_name = rest_of_path
    else:
        # If there's no slash, assume the entire path is the object name
        object_name = blob_path

    logger.info(f"Original blob_path: {blob_path}, Parsed object_name: {object_name}")

    # Always return the configured bucket name, not the one from the path
    return BUCKET_NAME, object_name
