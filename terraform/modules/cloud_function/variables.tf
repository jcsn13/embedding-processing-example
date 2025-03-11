variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region to deploy resources"
  type        = string
}

variable "cloud_function_name" {
  description = "Name of the Cloud Function"
  type        = string
}

variable "bucket_name" {
  description = "Name of the storage bucket for documents"
  type        = string
}

variable "memory" {
  description = "Memory allocation for the Cloud Function"
  type        = string
  default     = "2048MB"
}

variable "timeout" {
  description = "Timeout for the Cloud Function"
  type        = string
  default     = "540s"
}

variable "source_dir" {
  description = "Directory containing the Cloud Function source code"
  type        = string
  default     = "../cloud_function"
}

variable "runtime" {
  description = "Runtime for the Cloud Function"
  type        = string
  default     = "python310"
}

variable "service_account_email" {
  description = "Service account email for the Cloud Function"
  type        = string
}

# Variables for environment variables
variable "sectors" {
  description = "List of sectors to create Vector Search indexes for"
  type        = list(string)
  default     = ["accounting", "hr", "legal", "engineering", "sales", "marketing"]
}

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

variable "embedding_model_name" {
  description = "Name of the embedding model"
  type        = string
  default     = "text-multilingual-embedding-002"
}

variable "embedding_dimensions" {
  description = "Dimensions for the embedding model"
  type        = number
  default     = 768
}

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

variable "temp_directory" {
  description = "Temporary directory for file processing"
  type        = string
  default     = "/tmp"
}
