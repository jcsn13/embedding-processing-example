import logging
from typing import List, Dict, Any, Union
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
    TokenTextSplitter,
    SentenceTransformersTokenTextSplitter,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def chunk_text(text: str, strategy: str, options: Dict[str, Any] = None) -> List[str]:
    """
    Chunk text using the specified strategy with LangChain text splitters.

    Args:
        text (str): The text to chunk
        strategy (str): The chunking strategy to use
        options (Dict[str, Any], optional): Strategy-specific options

    Returns:
        List[str]: List of text chunks
    """
    if options is None:
        options = {}

    if strategy == "fixed_size":
        return fixed_size_chunking(text, **options)
    elif strategy == "semantic":
        return semantic_chunking(text, **options)
    elif strategy == "sliding_window":
        return sliding_window_chunking(text, **options)
    elif strategy == "hierarchical":
        return hierarchical_chunking(text, **options)
    else:
        raise ValueError(f"Unknown chunking strategy: {strategy}")


def fixed_size_chunking(text: str, chunk_size: int = 512) -> List[str]:
    """
    Divide text into chunks of fixed size using TokenTextSplitter.

    Args:
        text (str): The text to chunk
        chunk_size (int, optional): The maximum number of tokens per chunk

    Returns:
        List[str]: List of text chunks
    """
    splitter = TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=0)

    chunks = splitter.split_text(text)
    logger.info(f"Split text into {len(chunks)} fixed-size chunks")

    return chunks


def semantic_chunking(
    text: str, min_chunk_size: int = 100, max_chunk_size: int = 1000
) -> List[str]:
    """
    Divide text based on semantic boundaries using RecursiveCharacterTextSplitter.

    Args:
        text (str): The text to chunk
        min_chunk_size (int, optional): Minimum chunk size in tokens
        max_chunk_size (int, optional): Maximum chunk size in tokens

    Returns:
        List[str]: List of text chunks
    """
    # RecursiveCharacterTextSplitter splits on semantic boundaries
    # (paragraphs, then sentences, etc.)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_chunk_size,
        chunk_overlap=0,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = splitter.split_text(text)
    logger.info(f"Split text into {len(chunks)} semantic chunks")

    return chunks


def sliding_window_chunking(
    text: str, chunk_size: int = 512, overlap: int = 128
) -> List[str]:
    """
    Create overlapping chunks with a sliding window using TokenTextSplitter.

    Args:
        text (str): The text to chunk
        chunk_size (int, optional): The size of each chunk in tokens
        overlap (int, optional): The number of overlapping tokens between chunks

    Returns:
        List[str]: List of text chunks
    """
    splitter = TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)

    chunks = splitter.split_text(text)
    logger.info(
        f"Split text into {len(chunks)} sliding window chunks with {overlap} token overlap"
    )

    return chunks


def hierarchical_chunking(text: str, levels: List[str] = None) -> List[str]:
    """
    Create multi-level chunks using a combination of splitters.

    Args:
        text (str): The text to chunk
        levels (List[str], optional): Hierarchy levels to include

    Returns:
        List[str]: List of text chunks with hierarchy information
    """
    if levels is None:
        levels = ["document", "paragraph"]

    chunks = []

    # Document level
    if "document" in levels:
        # Get a summary/overview of the document (first 1000 chars)
        chunks.append(f"[DOCUMENT] {text[:1000]}...")

    # Section level chunks (larger semantic units)
    if "section" in levels:
        section_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200,
            separators=["\n## ", "\n### ", "\n#### ", "\n\n", "\n", ". "],
        )
        section_chunks = section_splitter.split_text(text)
        for i, chunk in enumerate(section_chunks):
            chunks.append(f"[SECTION {i+1}] {chunk}")

    # Paragraph level
    if "paragraph" in levels:
        paragraph_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=50, separators=["\n\n", "\n", ". "]
        )
        paragraph_chunks = paragraph_splitter.split_text(text)
        for i, chunk in enumerate(paragraph_chunks):
            chunks.append(f"[PARAGRAPH {i+1}] {chunk}")

    # Sentence level
    if "sentence" in levels:
        sentence_splitter = RecursiveCharacterTextSplitter(
            chunk_size=100, chunk_overlap=0, separators=[". ", "! ", "? ", "; "]
        )
        sentence_chunks = sentence_splitter.split_text(text)
        for i, chunk in enumerate(sentence_chunks):
            chunks.append(f"[SENTENCE {i+1}] {chunk}")

    logger.info(
        f"Created {len(chunks)} hierarchical chunks across {len(levels)} levels"
    )
    return chunks
