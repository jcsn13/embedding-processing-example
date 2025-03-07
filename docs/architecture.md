# System Architecture

```mermaid
flowchart TD
    A[Streamlit Frontend] -->|Upload Document| B[Cloud Storage]
    A -->|Trigger Processing| C[Cloud Function]
    B -->|Read Document| C
    C -->|Extract Text| D[Text Extraction]
    D -->|Process Text| E[Text Chunking]
    E -->|Generate Embeddings| F[Embedding Generation]
    F -->|Store Embeddings| G[Vertex AI Vector Search]
    F -->|Store Chunks| H[Firestore]
    
    subgraph "Processing Strategies"
        E1[Fixed-Size Chunking]
        E2[Semantic Chunking]
        E3[Sliding Window]
        E4[Hierarchical Chunking]
    end
    
    subgraph "Company Sectors"
        G1[Accounting Index]
        G2[HR Index]
        G3[Legal Index]
        G4[Engineering Index]
        G5[Sales Index]
    end
```

# Data Flow

```mermaid
sequenceDiagram
    participant User
    participant Streamlit
    participant CloudStorage
    participant CloudFunction
    participant VertexAI
    participant Firestore
    
    User->>Streamlit: Upload Document & Select Sector
    Streamlit->>CloudStorage: Store Document (Sector-Specific Path)
    Streamlit->>CloudFunction: Trigger Processing (With Sector Parameter)
    CloudFunction->>CloudStorage: Retrieve Document
    CloudFunction->>CloudFunction: Extract Text
    CloudFunction->>CloudFunction: Apply Chunking Strategy
    CloudFunction->>VertexAI: Generate Embeddings
    CloudFunction->>VertexAI: Store in Sector-Specific Vector Index
    CloudFunction->>Firestore: Store Chunks & Metadata (With Sector Info)
    CloudFunction->>Streamlit: Return Processing Status
    Streamlit->>User: Display Completion
