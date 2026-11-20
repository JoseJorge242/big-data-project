# Infraestrutura Aiven (PostgreSQL gerenciado)

Provisiona/gerencia o PostgreSQL usado pelo dashboard Streamlit.
O Docker local (`../../main.tf`) continua válido para desenvolvimento.

## Pré-requisitos
- Terraform >= 1.5
- Token de API do Aiven (Console > Perfil > Authentication > Create token)

## Uso
```bash
cd infra/aiven
cp terraform.tfvars.example terraform.tfvars   # preencher cloud_name e plan
export TF_VAR_aiven_api_token="SEU_TOKEN"       # PowerShell: $env:TF_VAR_aiven_api_token="SEU_TOKEN"
terraform init
```

### Serviço novo
```bash
terraform plan
terraform apply
```

### Serviço já existente (criado pelo console)
```bash
terraform import aiven_pg.transito SEU_PROJETO/SEU_SERVICO
terraform plan      # leia o plano: NÃO aplique se ele propuser recriar/destruir o serviço
```

## Carga e dashboard
```bash
terraform output -raw service_uri   # copiar para db_url (trocar postgres:// por postgresql+psycopg2://)
python scripts/carregar_postgres.py
streamlit run dashboard/app.py
```
Nunca versionar `terraform.tfvars`, `*.tfstate` nem o token.
