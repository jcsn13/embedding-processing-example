variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region to deploy resources"
  type        = string
}

variable "sectors" {
  description = "List of sectors to create Vector Search indexes for"
  type        = list(string)
  default     = ["accounting", "hr", "legal", "engineering", "sales", "marketing"]
}

variable "dimensions" {
  description = "Dimensions for the Vector Search index"
  type        = number
  default     = 768
}

variable "embedding_model" {
  description = "Embedding model to use for the Vector Search index"
  type        = string
  default     = "textembedding-gecko@latest"
}
