# Document Processing System

This project implements a document processing system that extracts text from uploaded documents, chunks the text using various strategies, generates embeddings, and stores them in sector-specific vector indexes.

## System Architecture

The system architecture is defined in `docs/architecture.md` as a Mermaid diagram. You can view this diagram by:

1. Opening the file in a Markdown viewer that supports Mermaid
2. Using an online Mermaid renderer like [Mermaid Live Editor](https://mermaid.live/)
3. Using VS Code with the Mermaid extension

The architecture consists of:

The system consists of the following components:

1. **Streamlit Frontend**: Allows users to upload documents, select processing strategies, and specify the company sector.
2. **Cloud Storage**: Stores uploaded documents temporarily.
3. **Cloud Function**: Processes documents, extracts text, chunks text, generates embeddings, and stores data.
4. **Vertex AI Vector Search**: Stores embeddings in sector-specific indexes.
5. **Firestore**: Stores text chunks and metadata for fast retrieval.

## Data Flow

1. User uploads a document and selects a sector via the Streamlit frontend
2. Document is stored in Cloud Storage in a sector-specific path
3. Cloud Function is triggered with document info and sector parameter
4. Cloud Function retrieves and processes the document
5. Text is extracted and chunked according to the selected strategy
6. Embeddings are generated for each chunk
7. Embeddings are stored in the sector-specific Vector Search index
8. Chunks and metadata are stored in Firestore with sector information
9. Processing status is returned to the frontend

## Document Processing

The system uses industry-standard libraries for document text extraction:

1. **Unstructured**: Primary document processing library that handles various document types
2. **PyPDF2 & pdfplumber**: For PDF text extraction with fallback mechanisms
3. **python-docx**: For Microsoft Word document processing
4. **LangChain Text Splitters**: For efficient and flexible text chunking

This approach ensures robust text extraction from various document formats and handles complex document structures effectively.

## Embedding Generation

The system uses Google's Vertex AI for embedding generation:

1. **Multilingual Embedding Model**: Uses the `text-multilingual-embedding-002` model for generating embeddings that work across multiple languages
2. **Task-Specific Embeddings**: Allows selection of different embedding task types to optimize for specific use cases:
   - `RETRIEVAL_QUERY`: For embedding search queries
   - `RETRIEVAL_DOCUMENT`: For embedding documents to be retrieved
   - `SEMANTIC_SIMILARITY`: For comparing text similarity
   - `CLASSIFICATION`: For text classification tasks
   - `CLUSTERING`: For grouping similar texts
   - `QUESTION_ANSWERING`: For question answering systems
   - `FACT_VERIFICATION`: For fact checking applications
   - `CODE_RETRIEVAL_QUERY`: For code search applications

The task type parameter helps the embedding model produce better vectors for the intended downstream application.

## Processing Strategies

The system supports multiple text chunking strategies using LangChain's text splitters:

1. **Fixed-Size Chunking**: Divides text into chunks of predetermined size using `TokenTextSplitter`.
2. **Semantic Chunking**: Divides text based on semantic boundaries using `RecursiveCharacterTextSplitter`.
3. **Sliding Window with Overlap**: Creates overlapping chunks with a sliding window using `TokenTextSplitter` with overlap.
4. **Hierarchical Chunking**: Creates multi-level chunks (document → section → paragraph) using multiple splitters.

## Sector-Specific Indexing

The system maintains separate Vector Search indexes for different company sectors (e.g., Accounting, HR, Legal). This approach:

- Enables compartmentalized knowledge access
- Improves security and access control
- Allows for sector-specific optimizations
- Facilitates better organization of company knowledge

## Project Structure

```
document_processing/
├── docs/                      # Documentation assets
│   └── architecture.png       # Architecture diagram
├── streamlit_app/             # Streamlit frontend
│   ├── app.py                 # Main Streamlit application
│   └── requirements.txt       # Frontend dependencies
├── cloud_function/            # Cloud Function code
│   ├── main.py                # Main entry point
│   ├── text_processing.py     # Text extraction utilities
│   ├── chunking.py            # Chunking strategies
│   ├── embeddings.py          # Embedding generation
│   ├── database.py            # Database operations
│   ├── config.py              # Configuration settings
│   └── requirements.txt       # Cloud Function dependencies
└── README.md                  # Project documentation
```

## Setup and Deployment

### Prerequisites

- Google Cloud Platform account
- Enabled APIs:
  - Cloud Functions
  - Cloud Storage
  - Firestore
  - Vertex AI
  - Vertex AI Vector Search

### Streamlit Frontend Deployment

1. Navigate to the `streamlit_app` directory
2. Install dependencies: `pip install -r requirements.txt`
3. Run locally: `streamlit run app.py`
4. For production, deploy to a service like Google App Engine or Cloud Run

### Deployment

#### Automated Deployment

The project includes a Makefile that automates the deployment of both the Cloud Function and the Streamlit app to Google Cloud Platform:

```bash
# Deploy infrastructure using variables from .env
make deploy
```

This will:
- Deploy the Cloud Function
- Deploy the Streamlit app to Cloud Run
- Create Vector Search indexes for each sector
- Update the configuration with the correct project-specific values
- Set up all necessary environment variables

#### Manual Deployment

##### Cloud Function Deployment

1. Navigate to the `cloud_function` directory
2. Deploy using gcloud CLI:
   ```
   gcloud functions deploy process_document \
     --runtime python39 \
     --trigger-http \
     --allow-unauthenticated \
     --memory=2048MB \
     --timeout=540s
   ```

##### Streamlit App Deployment to Cloud Run

1. Navigate to the `streamlit_app` directory
2. Build and deploy using gcloud CLI:
   ```
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/document-processing-app
   gcloud run deploy document-processing-app \
     --image gcr.io/YOUR_PROJECT_ID/document-processing-app \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --memory 2Gi \
     --set-env-vars="CLOUD_FUNCTION_URL=YOUR_CLOUD_FUNCTION_URL,BUCKET_NAME=YOUR_BUCKET_NAME"
   ```

##### Vector Search Index Setup

1. Create a Vector Search index for each company sector:
   ```
   gcloud ai vector-indexes create \
     --display-name=accounting-index \
     --location=us-central1 \
     --dimensions=768 \
     --embedding-model=textembedding-gecko@latest
   ```
2. Repeat for each sector (HR, Legal, etc.)

## Configuration

### Environment Variables

The project uses environment variables for configuration, which can be set in a `.env` file at the project root. An example file (`.env.example`) is provided as a template with detailed comments explaining each variable:

```bash
# Copy the example file to create your .env file
cp .env.example .env
# Edit the file with your specific configuration values
```

Key environment variables include:
- `PROJECT_ID`: Your Google Cloud project ID
- `REGION`: The Google Cloud region for your resources
- `BUCKET_NAME`: The Cloud Storage bucket for documents
- `SECTORS`: Space-separated list of business sectors (whitespace is automatically trimmed)
- Various configuration options for chunking strategies

The `.gitignore` file is configured to exclude the `.env` file from version control to prevent exposure of sensitive information.

### Sector Configuration

The system dynamically maps sectors (specified in the `SECTORS` environment variable) to Vector Search indexes:

```python
SECTOR_INDEX_MAPPING = {
    "accounting": "projects/your-project/locations/us-central1/indexes/accounting-index",
    "hr": "projects/your-project/locations/us-central1/indexes/hr-index",
    "legal": "projects/your-project/locations/us-central1/indexes/legal-index",
    # Dynamically created for each sector in the SECTORS environment variable
}
```

### Terraform Configuration

For infrastructure as code deployment, Terraform variables are automatically generated from environment variables:

```bash
# Deploy infrastructure using variables from .env
make deploy
```

This automatically creates the necessary `terraform/terraform.tfvars` file using values from your `.env` file. The `terraform.tfvars` file is included in `.gitignore` to prevent committing sensitive configuration values to version control.

## Security Considerations

- Implement IAM roles for sector-specific access
- Use Firestore security rules to enforce data access boundaries
- Consider encrypting sensitive documents in Cloud Storage
