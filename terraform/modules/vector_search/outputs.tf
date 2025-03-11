output "vector_search_indexes" {
  description = "Map of sector names to Vector Search index IDs"
  value = {
    for sector in var.sectors :
    sector => "projects/${var.project_id}/locations/${var.region}/indexes/${sector}-index"
  }
}
