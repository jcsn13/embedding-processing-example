import logging
from typing import List, Dict, Any, Tuple, Optional
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
from vertexai.language_models import TextEmbeddingModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Vertex AI
aiplatform.init()

# Valid task types for embeddings
VALID_TASK_TYPES = [
    "RETRIEVAL_QUERY",
    "RETRIEVAL_DOCUMENT",
    "SEMANTIC_SIMILARITY",
    "CLASSIFICATION",
    "CLUSTERING",
    "QUESTION_ANSWERING",
    "FACT_VERIFICATION",
    "CODE_RETRIEVAL_QUERY",
]


class EmbeddingGenerator:
    """Class to handle embedding generation using Vertex AI."""

    def __init__(
        self, model_name: str = "text-multilingual-embedding-002", dimensions: int = 768
    ):
        """
        Initialize the embedding generator.

        Args:
            model_name (str): The embedding model to use
            dimensions (int): The dimensionality of the embeddings
        """
        self.model_name = model_name
        self.dimensions = dimensions
        self.client = TextEmbeddingModel.from_pretrained(model_name)
        logger.info(f"Initialized embedding generator with model: {model_name}")

    def generate_embedding(
        self, text: str, task_type: str = "RETRIEVAL_DOCUMENT"
    ) -> List[float]:
        """
        Generate an embedding for a single text.

        Args:
            text (str): The text to embed
            task_type (str): The task type for the embedding

        Returns:
            List[float]: The embedding vector
        """
        if task_type not in VALID_TASK_TYPES:
            logger.warning(
                f"Invalid task_type: {task_type}. Using RETRIEVAL_DOCUMENT instead."
            )
            task_type = "RETRIEVAL_DOCUMENT"

        try:
            response = self.client.get_embeddings(
                [text], task_type=task_type, output_dimensionality=self.dimensions
            )

            if response and len(response) > 0 and response[0].values:
                return response[0].values
            else:
                logger.warning("Empty response from embedding model")
                return [0.0] * self.dimensions

        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            # Return zero vector as fallback
            return [0.0] * self.dimensions


def generate_embeddings(
    chunks: List[str], task_type: str = "RETRIEVAL_DOCUMENT"
) -> List[Tuple[str, List[float]]]:
    """
    Generate embeddings for a list of text chunks using Vertex AI.

    Args:
        chunks (List[str]): List of text chunks
        task_type (str): The task type for the embeddings

    Returns:
        List[Tuple[str, List[float]]]: List of (chunk, embedding) tuples
    """
    logger.info(
        f"Generating embeddings for {len(chunks)} chunks with task_type: {task_type}"
    )

    # Initialize the embedding generator
    generator = EmbeddingGenerator()

    # Use Vertex AI Text Embeddings API
    results = []

    # Process in batches to avoid API limits
    batch_size = 5  # Adjust based on API quotas and limits

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        batch_embeddings = _generate_batch_embeddings(batch, generator, task_type)

        # Combine chunks with their embeddings
        for j, embedding in enumerate(batch_embeddings):
            chunk_idx = i + j
            if chunk_idx < len(chunks):
                results.append((chunks[chunk_idx], embedding))

        logger.info(
            f"Processed batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}"
        )

    return results


def _generate_batch_embeddings(
    texts: List[str], generator: EmbeddingGenerator, task_type: str
) -> List[List[float]]:
    """
    Generate embeddings for a batch of texts using Vertex AI.

    Args:
        texts (List[str]): Batch of text chunks
        generator (EmbeddingGenerator): The embedding generator
        task_type (str): The task type for the embeddings

    Returns:
        List[List[float]]: List of embeddings
    """
    embeddings = []

    for text in texts:
        embedding = generator.generate_embedding(text, task_type)
        embeddings.append(embedding)

    return embeddings


def normalize_embedding(embedding: List[float]) -> List[float]:
    """
    Normalize an embedding vector to unit length.

    Args:
        embedding (List[float]): The embedding vector

    Returns:
        List[float]: Normalized embedding vector
    """
    import math

    # Calculate the magnitude
    magnitude = math.sqrt(sum(x**2 for x in embedding))

    # Normalize the vector
    if magnitude > 0:
        normalized = [x / magnitude for x in embedding]
        return normalized
    else:
        return embedding  # Return the original if magnitude is 0
