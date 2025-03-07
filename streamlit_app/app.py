import streamlit as st
import os
import tempfile
import requests
import json
import uuid
from google.cloud import storage

# Configuration
CLOUD_FUNCTION_URL = os.environ.get(
    "CLOUD_FUNCTION_URL",
    "https://your-region-your-project.cloudfunctions.net/process_document",
)
BUCKET_NAME = os.environ.get("BUCKET_NAME", "your-document-bucket")

# Initialize GCP clients
storage_client = storage.Client()

# Available sectors
SECTORS = ["accounting", "hr", "legal", "engineering", "sales", "marketing"]

# Available processing strategies
PROCESSING_STRATEGIES = {
    "fixed_size": "Fixed-Size Chunking",
    "semantic": "Semantic Chunking",
    "sliding_window": "Sliding Window with Overlap",
    "hierarchical": "Hierarchical Chunking",
}


def upload_to_gcs(file, sector):
    """Upload a file to Google Cloud Storage in the appropriate sector folder"""
    bucket = storage_client.bucket(BUCKET_NAME)
    document_id = str(uuid.uuid4())
    blob_path = f"{sector}/{document_id}/{file.name}"
    blob = bucket.blob(blob_path)

    with tempfile.NamedTemporaryFile() as temp:
        temp.write(file.getbuffer())
        temp.flush()
        blob.upload_from_filename(temp.name)

    return document_id, blob_path


def trigger_processing(
    document_id,
    blob_path,
    sector,
    processing_strategy,
    processing_options,
    embedding_task_type,
):
    """Trigger the Cloud Function to process the document"""
    payload = {
        "document_id": document_id,
        "blob_path": blob_path,
        "sector": sector,
        "processing_strategy": processing_strategy,
        "processing_options": processing_options,
        "embedding_task_type": embedding_task_type,
    }

    response = requests.post(CLOUD_FUNCTION_URL, json=payload)
    return response.json()


def main():
    st.title("Document Processing System")
    st.write("Upload documents for embedding generation and vector search indexing")

    # Sidebar for configuration
    st.sidebar.header("Processing Configuration")

    # Sector selection
    sector = st.sidebar.selectbox(
        "Select Company Sector",
        options=SECTORS,
        help="Choose the sector/department this document belongs to",
    )

    # Processing strategy selection
    processing_strategy = st.sidebar.selectbox(
        "Select Processing Strategy",
        options=list(PROCESSING_STRATEGIES.keys()),
        format_func=lambda x: PROCESSING_STRATEGIES[x],
        help="Choose how the document should be chunked",
    )

    # Processing options
    st.sidebar.subheader("Processing Options")

    # Different options based on strategy
    processing_options = {}

    if processing_strategy == "fixed_size":
        processing_options["chunk_size"] = st.sidebar.slider(
            "Chunk Size (tokens)", min_value=100, max_value=2000, value=512, step=50
        )

    elif processing_strategy == "sliding_window":
        processing_options["chunk_size"] = st.sidebar.slider(
            "Chunk Size (tokens)", min_value=100, max_value=2000, value=512, step=50
        )
        processing_options["overlap"] = st.sidebar.slider(
            "Overlap (tokens)", min_value=0, max_value=500, value=128, step=10
        )

    elif processing_strategy == "semantic":
        processing_options["min_chunk_size"] = st.sidebar.slider(
            "Minimum Chunk Size (tokens)",
            min_value=50,
            max_value=500,
            value=100,
            step=10,
        )
        processing_options["max_chunk_size"] = st.sidebar.slider(
            "Maximum Chunk Size (tokens)",
            min_value=500,
            max_value=2000,
            value=1000,
            step=50,
        )

    elif processing_strategy == "hierarchical":
        processing_options["levels"] = st.sidebar.multiselect(
            "Hierarchy Levels",
            options=["document", "section", "paragraph", "sentence"],
            default=["document", "paragraph"],
        )

    # Embedding options
    st.sidebar.subheader("Embedding Options")

    # Task type selection for embeddings
    embedding_task_types = [
        "RETRIEVAL_QUERY",
        "RETRIEVAL_DOCUMENT",
        "SEMANTIC_SIMILARITY",
        "CLASSIFICATION",
        "CLUSTERING",
        "QUESTION_ANSWERING",
        "FACT_VERIFICATION",
        "CODE_RETRIEVAL_QUERY",
    ]

    embedding_task_type = st.sidebar.selectbox(
        "Embedding Task Type",
        options=embedding_task_types,
        index=1,  # Default to RETRIEVAL_DOCUMENT
        help="Choose the task type for the embeddings. This helps the model produce better embeddings for your specific use case.",
    )

    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a document file",
        type=["pdf", "docx", "txt"],
        help="Upload a document to process",
    )

    if uploaded_file is not None:
        st.write(f"File uploaded: {uploaded_file.name}")

        # Process button
        if st.button("Process Document"):
            with st.spinner("Uploading document to Cloud Storage..."):
                document_id, blob_path = upload_to_gcs(uploaded_file, sector)

            with st.spinner("Processing document..."):
                result = trigger_processing(
                    document_id,
                    blob_path,
                    sector,
                    processing_strategy,
                    processing_options,
                    embedding_task_type,
                )

            if result.get("success"):
                st.success("Document processed successfully!")
                st.json(result)
            else:
                st.error("Error processing document")
                st.json(result)


if __name__ == "__main__":
    main()
