variable "aiven_api_token" {
  description = "Token de API do Aiven (Console > Perfil > Authentication > Create token)"
  type        = string
  sensitive   = true
}

variable "aiven_project" {
  description = "Nome do projeto no Aiven (aparece no host: <service>-<projeto>.aivencloud.com)"
  type        = string
}

variable "service_name" {
  description = "Nome do serviço PostgreSQL"
  type        = string
}

variable "cloud_name" {
  description = "Nuvem/região do serviço (copie do console do Aiven)"
  type        = string
}

variable "plan" {
  description = "Plano do serviço (copie do console; o plano gratuito tem nome próprio)"
  type        = string
}

variable "pg_version" {
  description = "Versão major do PostgreSQL"
  type        = string
  default     = "16"
}

variable "db_name" {
  description = "Banco de dados da aplicação"
  type        = string
  default     = "db_transito_brasil"
}
