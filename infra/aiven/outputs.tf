output "host" {
  value = aiven_pg.transito.service_host
}

output "port" {
  value = aiven_pg.transito.service_port
}

output "service_uri" {
  description = "URI de conexão (contém senha). Use: terraform output -raw service_uri"
  value       = aiven_pg.transito.service_uri
  sensitive   = true
}
