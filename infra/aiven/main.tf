resource "aiven_pg" "transito" {
  project      = var.aiven_project
  cloud_name   = var.cloud_name
  plan         = var.plan
  service_name = var.service_name

  pg_user_config {
    pg_version = var.pg_version

    ip_filter_object {
      network     = "0.0.0.0/0"
      description = "Streamlit Cloud (IP dinamico)"
    }
  }

  lifecycle {
    prevent_destroy = true
  }
}

resource "aiven_pg_database" "transito" {
  project       = var.aiven_project
  service_name  = aiven_pg.transito.service_name
  database_name = var.db_name
}
