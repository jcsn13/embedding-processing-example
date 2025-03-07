import logging
import uuid
from typing import List, Dict, Any, Tuple
from google.cloud import firestore
from google.cloud import aiplatform

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clients
firestore_client = firestore.Client()


def store_embeddings_in_vector_search(
    chunk_embeddings: List[Tuple[str, List[float]]], index_id: str
) -> List[str]:
    """
    Store embeddings in Vertex AI Vector Search.

    Args:
        chunk_embeddings (List[Tuple[str, List[float]]]): List of (chunk, embedding) tuples
        index_id (str): The Vector Search index ID

    Returns:
        List[str]: List of vector IDs
    """
    logger.info(
        f"Storing {len(chunk_embeddings)} embeddings in Vector Search index: {index_id}"
    )

    # Get the index
    index = aiplatform.MatchingEngineIndex(index_id)

    # Prepare data for indexing
    vector_ids = []
    embeddings = []

    for chunk, embedding in chunk_embeddings:
        # Generate a unique ID for each vector
        vector_id = str(uuid.uuid4())
        vector_ids.append(vector_id)
        embeddings.append(embedding)

    # Index the embeddings
    index.upsert_embeddings(embeddings=embeddings, ids=vector_ids)

    logger.info(f"Successfully stored {len(vector_ids)} embeddings in Vector Search")
    return vector_ids


def store_chunks_in_firestore(
    document_id: str,
    sector: str,
    chunks: List[str],
    vector_ids: List[str],
    metadata: Dict[str, Any] = None,
) -> List[str]:
    """
    Store text chunks in Firestore.

    Args:
        document_id (str): The original document ID
        sector (str): The company sector
        chunks (List[str]): List of text chunks
        vector_ids (List[str]): List of corresponding vector IDs
        metadata (Dict[str, Any], optional): Additional metadata

    Returns:
        List[str]: List of Firestore document references
    """
    if metadata is None:
        metadata = {}

    logger.info(
        f"Storing {len(chunks)} chunks in Firestore for document: {document_id}"
    )

    # Create a collection reference for the chunks
    chunks_collection = firestore_client.collection(
        f"sectors/{sector}/documents/{document_id}/chunks"
    )

    # Store document metadata
    document_ref = firestore_client.document(
        f"sectors/{sector}/documents/{document_id}"
    )
    document_ref.set(
        {
            "document_id": document_id,
            "sector": sector,
            "chunk_count": len(chunks),
            "metadata": metadata,
            "created_at": firestore.SERVER_TIMESTAMP,
        }
    )

    # Store each chunk with its vector ID
    chunk_refs = []
    batch = firestore_client.batch()

    for i, (chunk, vector_id) in enumerate(zip(chunks, vector_ids)):
        chunk_ref = chunks_collection.document(vector_id)
        chunk_refs.append(chunk_ref.path)

        batch.set(
            chunk_ref,
            {
                "text": chunk,
                "vector_id": vector_id,
                "document_id": document_id,
                "sector": sector,
                "chunk_index": i,
                "created_at": firestore.SERVER_TIMESTAMP,
            },
        )

        # Commit in batches of 500 (Firestore limit)
        if (i + 1) % 500 == 0:
            batch.commit()
            batch = firestore_client.batch()

    # Commit any remaining writes
    if len(chunks) % 500 != 0:
        batch.commit()

    logger.info(f"Successfully stored {len(chunk_refs)} chunks in Firestore")
    return chunk_refs


def retrieve_chunk_by_vector_id(sector: str, vector_id: str) -> Dict[str, Any]:
    """
    Retrieve a chunk from Firestore by its vector ID.

    Args:
        sector (str): The company sector
        vector_id (str): The vector ID

    Returns:
        Dict[str, Any]: The chunk data
    """
    # Query for the chunk across all documents in the sector
    query = (
        firestore_client.collection_group("chunks")
        .where("vector_id", "==", vector_id)
        .where("sector", "==", sector)
    )
    results = query.limit(1).stream()

    for doc in results:
        return doc.to_dict()

    return None


def retrieve_document_chunks(sector: str, document_id: str) -> List[Dict[str, Any]]:
    """
    Retrieve all chunks for a document.

    Args:
        sector (str): The company sector
        document_id (str): The document ID

    Returns:
        List[Dict[str, Any]]: List of chunk data
    """
    chunks_collection = firestore_client.collection(
        f"sectors/{sector}/documents/{document_id}/chunks"
    )
    results = chunks_collection.order_by("chunk_index").stream()

    return [doc.to_dict() for doc in results]
