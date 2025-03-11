variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region to deploy resources"
  type        = string
}

variable "firestore_api_enabled" {
  description = "A dependency to ensure the Firestore API is enabled"
  type        = any
}
