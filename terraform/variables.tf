variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "project_number" {
  description = "The GCP project number"
  type        = string
}

variable "region" {
  description = "The GCP region to deploy resources"
  type        = string
  default     = "us-central1"
}

variable "bucket_name" {
  description = "Name of the storage bucket for documents"
  type        = string
}

variable "cloud_function_name" {
  description = "Name of the Cloud Function"
  type        = string
  default     = "process-document"
}

variable "streamlit_app_name" {
  description = "Name of the Streamlit app"
  type        = string
  default     = "document-processing-app"
}

variable "function_memory" {
  description = "Memory allocation for the Cloud Function"
  type        = string
  default     = "2048MB"
}

variable "function_timeout" {
  description = "Timeout for the Cloud Function"
  type        = string
  default     = "540s"
}

variable "streamlit_memory" {
  description = "Memory allocation for the Streamlit app"
  type        = string
  default     = "2Gi"
}

variable "embedding_dimensions" {
  description = "Dimensions for the Vector Search index"
  type        = number
  default     = 768
}

variable "embedding_model" {
  description = "Embedding model to use for the Vector Search index"
  type        = string
  default     = "textembedding-gecko@latest"
}

variable "sectors" {
  description = "List of sectors to create Vector Search indexes for"
  type        = list(string)
  default     = ["accounting", "hr", "legal", "engineering", "sales", "marketing"]
}

# Chunking strategy variables
variable "fixed_size_chunk_size" {
  description = "Chunk size for fixed-size chunking strategy"
  type        = number
  default     = 512
}

variable "semantic_min_chunk_size" {
  description = "Minimum chunk size for semantic chunking strategy"
  type        = number
  default     = 100
}

variable "semantic_max_chunk_size" {
  description = "Maximum chunk size for semantic chunking strategy"
  type        = number
  default     = 1000
}

variable "sliding_window_chunk_size" {
  description = "Chunk size for sliding window chunking strategy"
  type        = number
  default     = 512
}

variable "sliding_window_overlap" {
  description = "Overlap size for sliding window chunking strategy"
  type        = number
  default     = 128
}

# Embedding model variables
variable "embedding_model_name" {
  description = "Name of the embedding model"
  type        = string
  default     = "text-multilingual-embedding-002"
}

# Firestore collection variables
variable "sectors_collection" {
  description = "Name of the Firestore sectors collection"
  type        = string
  default     = "sectors"
}

variable "documents_collection" {
  description = "Name of the Firestore documents collection"
  type        = string
  default     = "documents"
}

variable "chunks_collection" {
  description = "Name of the Firestore chunks collection"
  type        = string
  default     = "chunks"
}

# Other variables
variable "temp_directory" {
  description = "Temporary directory for file processing"
  type        = string
  default     = "/tmp"
}
