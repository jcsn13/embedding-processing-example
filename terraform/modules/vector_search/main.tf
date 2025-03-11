# Create Vector Search indexes for each sector
resource "google_vertex_ai_index" "sector_index" {
  for_each = toset(var.sectors)

  region       = var.region
  display_name = "${each.key}-index"
  description  = "Vector Search index for ${each.key} sector"

  metadata {
    contents_delta_uri = ""
    config {
      dimensions                  = var.dimensions
      approximate_neighbors_count = 150
      distance_measure_type       = "DOT_PRODUCT_DISTANCE"
      algorithm_config {
        tree_ah_config {
          leaf_node_embedding_count    = 1000
          leaf_nodes_to_search_percent = 10
        }
      }
    }
  }

  index_update_method = "STREAM_UPDATE"

  # The metadata_schema_uri is automatically set by the provider

  labels = {
    sector = each.key
  }
}
