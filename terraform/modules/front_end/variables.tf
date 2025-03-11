variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region to deploy resources"
  type        = string
}

variable "streamlit_app_name" {
  description = "Name of the Streamlit app"
  type        = string
}

variable "bucket_name" {
  description = "Name of the storage bucket for documents"
  type        = string
}

variable "cloud_function_url" {
  description = "URL of the Cloud Function"
  type        = string
}

variable "memory" {
  description = "Memory allocation for the Streamlit app"
  type        = string
  default     = "2Gi"
}

variable "service_account_email" {
  description = "Service account email for the Streamlit app"
  type        = string
}

variable "sectors" {
  description = "List of sectors to create Vector Search indexes for"
  type        = list(string)
  default     = ["accounting", "hr", "legal", "engineering", "sales", "marketing"]
}

variable "source_dir" {
  description = "Directory containing the Streamlit app source code"
  type        = string
  default     = "../streamlit_app"
}
