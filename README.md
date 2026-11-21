# 📊 Análise Integrada de Trânsito e Mortalidade no Brasil

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-ETL-150458?logo=pandas&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql&logoColor=white)
![MinIO](https://img.shields.io/badge/MinIO-S3%20Data%20Lake-C72E49?logo=minio&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-IaC-7B42BC?logo=terraform&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containers-2496ED?logo=docker&logoColor=white)
![Aiven](https://img.shields.io/badge/Aiven-PostgreSQL%20gerenciado-FF3554)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Gr%C3%A1ficos-3F4F75?logo=plotly&logoColor=white)

Solução completa de **Engenharia de Dados** para ingestão, tratamento, modelagem, carga relacional e provisionamento de infraestrutura como código (IaC) a partir de três bases públicas oficiais do governo brasileiro: acidentes rodoviários (**PRF**), mortalidade (**SIM/DATASUS**) e indicadores de óbitos no trânsito (**MGDI / Ministério da Saúde**).

O recorte analítico é orientado pela **ODS 5 (Igualdade de Gênero)** e pela **ODS 18 (Igualdade Étnico-Racial)**, e os resultados são apresentados em um **dashboard interativo** conectado diretamente ao banco PostgreSQL gerenciado no **Aiven**.

---

## 🚀 Acesso Rápido

| | |
|---|---|
| **🔗 Dashboard publicado** | https://big-data-project-sbqwmipsjzjwtopxganx2j.streamlit.app/ |
| **📖 Detalhes e indicadores** | [Seção 11 – Dashboard Analítico](#11-dashboard-analítico) |
| **🧠 Análise crítica (ODS 5 e 18)** | [Seção 12 – Análise Crítica](#12-análise-crítica-ods-5-e-ods-18) |
| **▶️ Rodar localmente** | Comando único abaixo (requer o `secrets.toml` descrito na [seção 13](#13-execução-e-deploy-do-dashboard)) |

```bash
pip install -r dashboard/requirements.txt && streamlit run dashboard/app.py
```

---

## Sumário

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Estrutura do Repositório](#estrutura-do-repositório)
- [1. Dados Utilizados](#1-dados-utilizados)
- [2. Tratamento Realizado (ETL)](#2-tratamento-realizado-etl)
- [3. Modelagem dos Dados](#3-modelagem-dos-dados)
- [4. Infraestrutura como Código (IaC)](#4-infraestrutura-como-código-iac)
- [5. Justificativa das Escolhas Tecnológicas](#5-justificativa-das-escolhas-tecnológicas)
- [6. Guia de Execução e Reprodução](#6-guia-de-execução-e-reprodução)
- [7. Exemplos de Consultas SQL](#7-exemplos-de-consultas-sql)
- [8. Solução de Problemas](#8-solução-de-problemas)
- [9. Segurança](#9-segurança)
- [10. Próximos Passos](#10-próximos-passos)
- [11. Dashboard Analítico](#11-dashboard-analítico)
- [12. Análise Crítica: ODS 5 e ODS 18](#12-análise-crítica-ods-5-e-ods-18)
- [13. Execução e Deploy do Dashboard](#13-execução-e-deploy-do-dashboard)
- [Licença e Autoria](#licença-e-autoria)

---

## Visão Geral

O projeto responde a uma pergunta central: **como integrar fontes heterogêneas de dados de trânsito e saúde pública em uma base analítica confiável e reproduzível?**

Para isso, a solução:

1. **Ingere** arquivos CSV brutos com problemas reais de qualidade (encodings mistos, metadados no cabeçalho, valores ausentes representados por símbolos).
2. **Trata** e padroniza os dados com scripts Python, preservando os arquivos originais.
3. **Modela** os dados em tabelas relacionais prontas para análise.
4. **Provisiona** a infraestrutura (PostgreSQL + MinIO) de forma declarativa com Terraform e Docker.
5. **Carrega** os dados tratados no PostgreSQL de maneira automatizada.
6. **Visualiza** os dados em um **dashboard Streamlit** publicado, conectado diretamente ao PostgreSQL no Aiven, com 4 indicadores-chave, 4 gráficos analíticos e filtros dinâmicos (seção 11).

---

## Arquitetura

O projeto adota **armazenamento em camadas** (Data Lake + Relacional), no padrão Bronze / Silver / Gold:

```text
[Dados Brutos / Bronze]      [Dados Tratados / Silver]      [Camada Analítica / Gold]
 data/versao.original/  ──>   data/versao.resultado/   ──>   PostgreSQL & MinIO S3
 (CSVs brutos imutáveis)      (CSVs limpos em UTF-8)         (Tabelas estruturadas)
```

| Camada | Local | Conteúdo |
|--------|-------|----------|
| **Bronze** | `data/versao.original/` | Arquivos originais, sem alterações (imutáveis, para auditoria) |
| **Silver** | `data/versao.resultado/` | CSVs limpos, padronizados e em UTF-8 |
| **Gold** | PostgreSQL (`db_transito_brasil`) e MinIO | Tabelas estruturadas para consulta e dashboards |

---

## Estrutura do Repositório

```text
big-data-project/
├── dashboard/
│   ├── app.py                    # Dashboard Streamlit (consulta o PostgreSQL)
│   └── requirements.txt          # Dependências do dashboard
├── data/
│   ├── versao.original/          # Bronze: CSVs brutos (SIM, PRF, MGDI)
│   └── versao.resultado/         # Silver: CSVs tratados
├── scripts/
│   ├── TratarDadosSIM.py         # ETL do SIM/DATASUS
│   ├── TratarAcidentes2021a25.py # ETL dos acidentes PRF (2021-2025)
│   ├── TratarMgdi.py             # ETL do MGDI (processamento em chunks)
│   └── carregar_postgres.py      # Carga das tabelas no PostgreSQL
├── infra/
│   └── aiven/                    # Terraform do PostgreSQL gerenciado (Aiven) + README próprio
├── main.tf                       # Infraestrutura (Docker via Terraform)
├── terraform.tfvars.example      # Modelo das variáveis sensíveis
├── .gitignore                    # Bloqueia terraform.tfvars e artefatos locais
└── README.md
```

---

## 1. Dados Utilizados

A solução consolida dados de três fontes públicas oficiais:

### 1.1 Sistema de Informações sobre Mortalidade (SIM / MS – DATASUS)

| Item | Descrição |
|------|-----------|
| **Arquivos** | `sim_cnv_*.csv` |
| **Recorte** | Série histórica por grupo de causa básica (CID-10) e desagregação demográfica |
| **Formato** | CSV exportado do TABNET, com metadados no cabeçalho e codificação `latin1` |
| **Dimensões** | Óbitos por **Gênero** (Masc, Fem, Ign) e **Raça/Cor** (Branca, Preta, Amarela, Parda, Indígena, Ignorado) |

### 1.2 Acidentes de Trânsito Rodoviário (PRF)

| Item | Descrição |
|------|-----------|
| **Arquivos** | `acidentes2021.csv` a `acidentes2025.csv` |
| **Recorte** | Anos de **2021 a 2025** |
| **Conteúdo** | Microdados por data (`data_inversa`), localização (`uf`, `municipio`), causa/tipo do acidente, perfil do envolvido (`idade`, `sexo`, `tipo_envolvido`) e severidade (`estado_fisico`, `mortos`) |

### 1.3 Indicadores de Óbitos no Trânsito (MGDI / Ministério da Saúde)

| Item | Descrição |
|------|-----------|
| **Arquivo** | `mgdi_ms_g0g.csv` |
| **Recorte** | Dados municipais consolidados de óbitos no trânsito e estimativas populacionais |
| **Conteúdo** | Mortalidade por modalidade de transporte (pedestres, ciclistas, motociclistas, automóveis/ônibus) e faixas etárias |
| **Observação** | Base volumosa; exige processamento em blocos para não esgotar a memória RAM |

---

## 2. Tratamento Realizado (ETL)

### 2.1 Problemas Identificados

| # | Problema | Impacto |
|---|----------|---------|
| 1 | **Inconsistência de encodings** (`latin1` e `utf-8` misturados) | Erros de *mojibake* (ex.: `Ã`, `Â`) |
| 2 | **Cabeçalhos e metadados** nos arquivos do SIM | Linhas informativas antes da tabela real |
| 3 | **Valores ausentes e formatação** | Hífen (`-`) usado para indicar zero; tipos numéricos inconsistentes |
| 4 | **Volumetria elevada** (MGDI) | Alto consumo de RAM ao manipular a base em memória |

### 2.2 Scripts e Transformações

#### `scripts/TratarDadosSIM.py`
- Leitura ignorando o cabeçalho de metadados (`skiprows=3`) e extração do ano via expressão regular.
- Filtragem por regex no campo `Grupo CID10` para manter apenas causas ligadas ao trânsito: `transporte|Pedestre|Ciclista|Motociclista|triciclo`.
- Substituição de `-` por `0` e conversão segura para inteiros (`pd.to_numeric`).
- **Saídas:** `data/versao.resultado/tratado_sim_genero.csv` e `data/versao.resultado/tratado_sim_raca.csv`.

#### `scripts/TratarAcidentes2021a25.py`
- *Parsing* da coluna `data_inversa` para criar a coluna numérica `Ano`.
- Seleção estrita dos atributos essenciais (`causa_acidente`, `tipo_acidente`, `classificacao_acidente`, `estado_fisico`, `mortos`, entre outros).
- Normalização de nulos em atributos categóricos (`sexo` ausente preenchido como `'Não Informado'`).
- Consolidação dos cinco anos em uma única base.
- **Saída:** `data/versao.resultado/tratado_todos_acidentes2021a2025.csv`.

#### `scripts/TratarMgdi.py`
- Processamento otimizado em blocos de memória (`chunksize=100_000`).
- Função personalizada para correção de acentuação e padronização de encodings.
- Exclusão de registros totalmente vazios (`dropna(how="all")`).
- **Saída:** `data/versao.resultado/mgdi_ms_g0g_tratado.csv`.

#### `scripts/carregar_postgres.py`
- Leitura das bases tratadas em `data/versao.resultado/`.
- Carga automatizada dos DataFrames via `SQLAlchemy` / `psycopg`, criando as tabelas diretamente no PostgreSQL.

### 2.3 Fluxo de Execução do ETL

```text
SIM (latin1, metadados)  ──> TratarDadosSIM.py          ──> tratado_sim_genero.csv
                                                         └─> tratado_sim_raca.csv
PRF (2021–2025)          ──> TratarAcidentes2021a25.py  ──> tratado_todos_acidentes2021a2025.csv
MGDI (volumoso)          ──> TratarMgdi.py (chunks)     ──> mgdi_ms_g0g_tratado.csv
                                         │
                                         ▼
                              carregar_postgres.py ──> PostgreSQL (db_transito_brasil)
```

---

## 3. Modelagem dos Dados

### Banco Relacional: `db_transito_brasil`

#### `tb_sim_genero`
| Coluna | Tipo |
|--------|------|
| `Ano` | INT |
| `Grupo CID10` | VARCHAR |
| `Masc` | INT |
| `Fem` | INT |
| `Ign` | INT |
| `Total` | INT |

#### `tb_sim_raca`
| Coluna | Tipo |
|--------|------|
| `Ano` | INT |
| `Grupo CID10` | VARCHAR |
| `Branca` | INT |
| `Preta` | INT |
| `Amarela` | INT |
| `Parda` | INT |
| `Indigena` | INT |
| `Ignorado` | INT |
| `Total` | INT |

#### `tb_acidentes`
| Coluna | Tipo |
|--------|------|
| `Ano` | INT |
| `data_inversa` | DATE |
| `uf` | VARCHAR |
| `municipio` | VARCHAR |
| `causa_acidente` | VARCHAR |
| `tipo_acidente` | VARCHAR |
| `classificacao_acidente` | VARCHAR |
| `tipo_envolvido` | VARCHAR |
| `estado_fisico` | VARCHAR |
| `idade` | INT |
| `sexo` | VARCHAR |
| `mortos` | INT |

#### `tb_mgdi_indicadores`
| Coluna | Tipo |
|--------|------|
| `indicador` | VARCHAR |
| `ano` | INT |
| `uf` | VARCHAR |
| `codigo_municipio` | INT |
| `nome_municipio` | VARCHAR |
| `sexo` | VARCHAR |
| `faixa_etaria` | VARCHAR |
| `obitos_transito` | INT |
| `obitos_pedestres` | INT |
| `obitos_ciclistas` | INT |
| `obitos_motociclistas` | INT |

### Relacionamentos Analíticos

As tabelas não possuem chaves estrangeiras formais (são fatos agregados de fontes distintas), mas podem ser cruzadas por **ano** e **UF**:

```text
tb_acidentes.Ano / uf  ◄──►  tb_mgdi_indicadores.ano / uf
tb_sim_genero.Ano      ◄──►  tb_sim_raca.Ano  (mesmo Grupo CID10)
```

---

## 4. Infraestrutura como Código (IaC)

A infraestrutura é provisionada de forma declarativa com **Terraform** sobre contêineres **Docker**.

### Serviços

| Serviço | Imagem | Função | Portas |
|---------|--------|--------|--------|
| **PostgreSQL** | `postgres:15-alpine` | Banco relacional analítico | `5432` |
| **MinIO** | `coollabsio/minio:latest` | Data Lake local compatível com a API AWS S3 | `9000` (API) / `9001` (Console Web) |

### Recursos definidos em `main.tf`

| Recurso | Descrição |
|---------|-----------|
| `docker_network.transito_network` | Rede interna isolada (`rede_dados_transito`) |
| `docker_volume.postgres_data` | Volume persistente do PostgreSQL |
| `docker_volume.minio_data` | Volume persistente do MinIO |
| `docker_container.postgres_db` | Contêiner do PostgreSQL (porta externa `5432`) |
| `docker_container.minio_s3` | Contêiner do MinIO (portas `9000` e `9001`) |


### Nuvem: PostgreSQL gerenciado no Aiven (`infra/aiven/`)

Além do ambiente local acima, o banco consumido pelo **dashboard publicado** é provisionado no **Aiven** com Terraform, em um módulo separado (`infra/aiven/`) também versionado neste repositório. O Docker local continua válido para desenvolvimento.

| Recurso | Descrição |
|---------|-----------|
| `aiven_pg.transito` | Serviço PostgreSQL (projeto, nuvem/região, plano e nome vindos de variáveis; versão padrão `16`). Possui `prevent_destroy = true` para impedir remoção acidental |
| `aiven_pg_database.transito` | Banco de dados `db_transito_brasil` dentro do serviço |
| `ip_filter_object` | Libera `0.0.0.0/0`, pois o Streamlit Cloud usa IPs dinâmicos (ver [seção 13.4](#134-segurança)) |

| Variável | Obrigatória | Descrição |
|----------|-------------|-----------|
| `aiven_api_token` | sim (`sensitive`) | Token de API do Aiven. Informar por `TF_VAR_aiven_api_token`, nunca em arquivo |
| `aiven_project` | sim | Nome do projeto no Aiven |
| `service_name` | sim | Nome do serviço PostgreSQL |
| `cloud_name` | sim | Nuvem/região (copiar do console do Aiven) |
| `plan` | sim | Plano do serviço (copiar do console do Aiven) |
| `pg_version` | não (`16`) | Versão major do PostgreSQL |
| `db_name` | não (`db_transito_brasil`) | Banco de dados da aplicação |

**Outputs:** `host`, `port` e `service_uri` (este marcado como `sensitive`; obter com `terraform output -raw service_uri`).

```bash
cd infra/aiven
cp terraform.tfvars.example terraform.tfvars    # preencher cloud_name e plan
export TF_VAR_aiven_api_token="SEU_TOKEN"       # PowerShell: $env:TF_VAR_aiven_api_token="SEU_TOKEN"
terraform init
terraform plan
terraform apply
```

O passo a passo completo (inclusive como **importar** um serviço criado manualmente pelo console) está em [`infra/aiven/README.md`](infra/aiven/README.md). A carga dos dados no Aiven e a publicação do dashboard estão na [seção 13](#13-execução-e-deploy-do-dashboard).

---

## 5. Justificativa das Escolhas Tecnológicas

| Decisão | Justificativa |
|---------|---------------|
| **Python + Pandas + SQLAlchemy** | Suporte nativo a *parsing* de encodings e expressões regulares; integração direta com PostgreSQL via SQLAlchemy e drivers `psycopg`. |
| **Processamento em chunks** | A leitura em blocos (`chunksize=100_000`) da base MGDI evita falhas por falta de memória (*Out-Of-Memory*) e permite rodar em qualquer ambiente. |
| **Arquitetura em camadas (Bronze / Silver / Gold)** | Preserva o arquivo bruto para auditoria, isola os CSVs saneados e expõe somente dados consolidados na camada analítica. |
| **PostgreSQL 15** | Ideal para consultas estruturadas com agregações (`GROUP BY`), cruzamentos por UF/município e integração com ferramentas de BI. |
| **MinIO (S3 local)** | Simula o armazenamento de objetos da nuvem (AWS S3) sem custo de infraestrutura. |
| **Terraform + Docker** | Reprodutibilidade exata: banco e Data Lake sobem de forma unificada e determinística, com versionamento da infraestrutura. |

---

## 6. Guia de Execução e Reprodução

### Pré-requisitos

- **Docker Engine / Docker Desktop** em execução
- **Terraform** v1.5+
- **Python 3** instalado
- Bases originais disponíveis (SIM, PRF e MGDI)

### Passo a Passo

**1. Clonar o repositório**

```bash
git clone https://github.com/celesteadoq/big-data-project.git
cd big-data-project
```

**2. Configurar as variáveis de segurança**

Copie o arquivo de exemplo para criar o arquivo local (ignorado pelo `.gitignore`):

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edite o `terraform.tfvars` e defina suas senhas e credenciais.

**3. Provisionar a infraestrutura**

```bash
terraform init
terraform apply -auto-approve
```

**4. Instalar as dependências do Python**

```bash
pip3 install pandas psycopg2-binary psycopg sqlalchemy --break-system-packages
```

> 💡 **Alternativa recomendada:** use um ambiente virtual para não alterar o Python do sistema:
> ```bash
> python3 -m venv .venv
> source .venv/bin/activate        # Windows: .venv\Scripts\activate
> pip install pandas psycopg2-binary psycopg sqlalchemy
> ```

**5. Executar os scripts de tratamento (ETL)**

Com as bases originais em `data/versao.original/`:

```bash
python3 scripts/TratarDadosSIM.py
python3 scripts/TratarAcidentes2021a25.py
python3 scripts/TratarMgdi.py
```

**6. Carregar as tabelas no PostgreSQL**

```bash
python3 scripts/carregar_postgres.py
```

**7. Acessar os serviços**

| Serviço | Endereço | Observação |
|---------|----------|------------|
| **PostgreSQL** | `localhost:5432` | Banco: `db_transito_brasil` |
| **MinIO (Console)** | http://localhost:9001 | Use as credenciais definidas no `terraform.tfvars` |
| **MinIO (API S3)** | http://localhost:9000 | Compatível com clientes AWS S3 |

### Verificando a Carga

```bash
psql -h localhost -p 5432 -U <seu_usuario> -d db_transito_brasil -c "\dt"
```

### Encerrando o Ambiente

```bash
terraform destroy
```

> ⚠️ Isso remove os contêineres e a rede. Confira no `main.tf` se os volumes também serão removidos antes de executar, caso queira preservar os dados.

---

## 7. Exemplos de Consultas SQL

> Os nomes de colunas com maiúsculas ou espaços (`Ano`, `Grupo CID10`) precisam de aspas duplas no PostgreSQL.

**Total de mortos em acidentes por ano**

```sql
SELECT "Ano", SUM(mortos) AS total_mortos
FROM tb_acidentes
GROUP BY "Ano"
ORDER BY "Ano";
```

**Top 10 UFs com mais mortos (2021–2025)**

```sql
SELECT uf, SUM(mortos) AS total_mortos
FROM tb_acidentes
GROUP BY uf
ORDER BY total_mortos DESC
LIMIT 10;
```

**Principais causas de acidentes**

```sql
SELECT causa_acidente, COUNT(*) AS ocorrencias
FROM tb_acidentes
GROUP BY causa_acidente
ORDER BY ocorrencias DESC
LIMIT 10;
```

**Óbitos no trânsito por gênero e ano (SIM)**

```sql
SELECT "Ano",
       SUM("Masc") AS masculino,
       SUM("Fem")  AS feminino,
       SUM("Total") AS total
FROM tb_sim_genero
GROUP BY "Ano"
ORDER BY "Ano";
```

**Óbitos por raça/cor (SIM)**

```sql
SELECT "Ano",
       SUM("Branca") AS branca,
       SUM("Preta")  AS preta,
       SUM("Parda")  AS parda
FROM tb_sim_raca
GROUP BY "Ano"
ORDER BY "Ano";
```

**Óbitos de motociclistas por UF (MGDI)**

```sql
SELECT uf, ano, SUM(obitos_motociclistas) AS obitos_motos
FROM tb_mgdi_indicadores
GROUP BY uf, ano
ORDER BY ano, obitos_motos DESC;
```

**Cruzamento PRF × MGDI por UF e ano**

```sql
SELECT a."Ano", a.uf,
       SUM(a.mortos)            AS mortos_prf,
       SUM(m.obitos_transito)   AS obitos_mgdi
FROM tb_acidentes a
JOIN tb_mgdi_indicadores m
  ON m.uf = a.uf AND m.ano = a."Ano"
GROUP BY a."Ano", a.uf
ORDER BY a."Ano", a.uf;
```

> ⚠️ O cruzamento acima é ilustrativo: as fontes têm metodologias diferentes (a PRF cobre apenas rodovias federais; o MGDI/SIM cobre óbitos em todo o território). Se `tb_mgdi_indicadores` tiver várias linhas por UF/ano, agregue-a em uma subconsulta antes do `JOIN` para evitar duplicação de valores.

---

## 8. Solução de Problemas

| Sintoma | Causa provável | Solução |
|---------|----------------|---------|
| Caracteres como `Ã` ou `Â` nos dados | Leitura com encoding incorreto | Confirme que o arquivo bruto é `latin1` e use os scripts de tratamento antes da carga |
| `Cannot connect to the Docker daemon` | Docker não está em execução | Inicie o Docker Desktop / serviço do Docker |
| `connection refused` na porta `5432` | Contêiner parado ou porta ocupada por outro PostgreSQL | Verifique com `docker ps`; pare o serviço local ou altere a porta externa no `main.tf` |
| `MemoryError` ao processar o MGDI | Leitura da base inteira em memória | Mantenha o `chunksize=100_000` (ou reduza-o) |
| `error: externally-managed-environment` no `pip` | Python gerenciado pelo sistema | Use `--break-system-packages` ou, preferencialmente, um ambiente virtual |
| Erro de autenticação no PostgreSQL | Credenciais divergentes do `terraform.tfvars` | Use exatamente os valores definidos no `terraform.tfvars` |
| Arquivo `data/versao.resultado/` vazio | Etapa de ETL não executada ou bases ausentes | Confirme os arquivos em `data/versao.original/` e rode os scripts de tratamento |

---

## 9. Segurança

- O arquivo **`terraform.tfvars`** contém credenciais e **nunca deve ser versionado** (já está no `.gitignore`).
- Use apenas o **`terraform.tfvars.example`** com valores fictícios no repositório.
- Os serviços expõem portas em `localhost` para uso **local/desenvolvimento**. Não exponha `5432`, `9000` ou `9001` diretamente na internet.
- Utilize senhas fortes e diferentes para o PostgreSQL e o MinIO.
- Os dados são públicos e agregados/anonimizados pelas fontes oficiais, mas respeite os termos de uso de cada órgão.

---

## 10. Próximos Passos

- [ ] Orquestração do pipeline completo (ex.: Apache Airflow ou Prefect)
- [ ] Envio automatizado dos CSVs tratados ao bucket MinIO
- [ ] Criação de chaves, índices e tabelas-dimensão (UF, município, tempo) no PostgreSQL
- [ ] Testes de qualidade de dados (ex.: Great Expectations)
- [x] Dashboard analítico (Streamlit + Plotly, conectado ao Aiven) — ver [seção 11](#11-dashboard-analítico)
- [ ] Pipeline de CI para validar scripts e `terraform validate`

---

## 11. Dashboard Analítico

O dashboard (`dashboard/app.py`) é uma aplicação **Streamlit** que executa consultas SQL parametrizadas, via SQLAlchemy, **diretamente no PostgreSQL do Aiven**. Não há arquivos intermediários: tudo o que aparece na tela vem do banco.

**🔗 Dashboard publicado:** https://big-data-project-sbqwmipsjzjwtopxganx2j.streamlit.app/

### 11.1 Arquitetura de implantação

```mermaid
flowchart LR
    ETL["ETL Python +<br/>carregar_postgres.py"] --> PG
    subgraph Aiven["Aiven (Terraform: infra/aiven/)"]
        PG[("PostgreSQL 16<br/>db_transito_brasil")]
    end
    subgraph Cloud["Streamlit Community Cloud"]
        APP["dashboard/app.py<br/>Streamlit + Plotly"]
    end
    USER(["Usuário no navegador"])
    PG -- "SQL parametrizado (SQLAlchemy)<br/>cache de 60 s" --> APP
    APP -- "filtros e gráficos" --> USER
```

### 11.2 Interface

![Dashboard publicado: indicadores-chave e gráficos 1 e 2](docs/img/dashboard-1.png)

![Dashboard publicado: gráficos 3 e 4](docs/img/dashboard-2.png)

*Capturas do dashboard publicado, com os filtros padrão (período 2021–2025, todas as UFs, sexos e faixas etárias, grupo CID-10 "Acidentes de transporte").*

Estrutura da tela:

```text
┌──────────────┬──────────────────────────────────────────────────────────┐
│  FILTROS     │  Trânsito e mortalidade no Brasil                        │
│              │  ODS 5 e ODS 18 · SIM/DATASUS, PRF e MGDI/MS             │
│ Período      ├───────────────┬───────────────┬───────────────┬──────────┤
│ UF           │ Óbitos no     │ % mulheres    │ % pretos +    │ UF com   │
│ Sexo         │ trânsito (SIM)│               │ pardos        │ mais     │
│ Faixa etária │               │               │               │ óbitos   │
│ Grupo CID-10 ├───────────────┴───────┬───────┴───────────────┴──────────┤
│              │ 1 · Óbitos por sexo   │ 2 · Taxa por 100 mil hab. por    │
│              │     por ano           │     sexo e faixa etária          │
│              ├───────────────────────┼──────────────────────────────────┤
│              │ 3 · Óbitos por        │ 4 · Ranking de UFs: óbitos em    │
│              │     raça/cor (% ano)  │     rodovias federais (PRF)      │
│              ├───────────────────────┴──────────────────────────────────┤
│              │ ▸ Ver dados consultados (tabelas por fonte)              │
└──────────────┴──────────────────────────────────────────────────────────┘
```

### 11.3 Os 4 indicadores-chave (cartões no topo)

| # | Indicador | Fonte | Como é calculado | ODS |
|---|-----------|-------|------------------|-----|
| **1** | **Óbitos no trânsito (SIM)** | `tb_sim_genero` | `SUM(total)` no período e nos grupos CID-10 selecionados. Por padrão usa o grupo **"Acidentes de transporte"**, que já é o total | 5 e 18 |
| **2** | **% mulheres** | `tb_sim_genero` | `SUM(fem) ÷ SUM(total)` com os mesmos filtros | **5** |
| **3** | **% pretos + pardos** | `tb_sim_raca` | `(SUM(preta) + SUM(parda)) ÷ soma de todas as categorias de raça/cor`, **incluindo "ignorado"** no denominador | **18** |
| **4** | **UF com mais óbitos (PRF)** | `tb_acidentes` | UF com o maior número de pessoas em estado físico "Óbito" no período (apenas rodovias federais) | 5 |

### 11.4 Os 4 gráficos analíticos

| # | Gráfico | Fonte | O que mostra | Detalhes de cálculo |
|---|---------|-------|--------------|---------------------|
| **1** | **Óbitos por sexo ao longo dos anos** (barras agrupadas) | SIM | Evolução anual de óbitos masculinos e femininos (**ODS 5**) | Soma por ano de `masc` e `fem` |
| **2** | **Taxa por 100 mil hab. por sexo e faixa etária** (barras agrupadas) | MGDI | Risco de morrer no trânsito por sexo em cada faixa etária (**ODS 5**) | `Σ obitos_transito ÷ Σ populacao_estimada × 100.000`. Usa **taxas**, não contagens, pois as faixas etárias têm larguras diferentes |
| **3** | **Óbitos por raça/cor** (barras empilhadas, 100 %) | SIM | Composição racial dos óbitos por ano (**ODS 18**) | A fatia "ignorado" funciona como indicador de qualidade do registro |
| **4** | **Ranking de UFs: óbitos em rodovias federais** (barras horizontais, top 10) | PRF | UFs com mais óbitos; o *hover* mostra nº de acidentes e óbitos femininos (**ODS 5**) | Óbitos = pessoas com `estado_fisico` "Óbito"; acidentes = `COUNT(DISTINCT id)` |

O expansor **"Ver dados consultados"**, no fim da página, exibe as tabelas retornadas pelo banco, o que permite auditar os números e demonstrar a consulta em tempo real.

### 11.5 Filtros dinâmicos (barra lateral)

| Filtro | Tipo | Afeta |
|--------|------|-------|
| **Período** | Slider de intervalo de anos | Todos os indicadores e gráficos |
| **UF (PRF e MGDI)** | Seleção única (`Todas` + UFs) | Indicador 4 e gráficos 2 e 4 (o SIM não tem UF) |
| **Sexo (MGDI)** | Multisseleção | Gráfico 2 |
| **Faixa etária (MGDI)** | Multisseleção | Gráfico 2 |
| **Grupo CID-10 (SIM)** | Multisseleção | Indicadores 1 a 3 e gráficos 1 e 3 |

> **Atenção ao filtro de Grupo CID-10:** "Acidentes de transporte" é o **total**. Para detalhar por subgrupo (pedestre, motociclista etc.), marque apenas os subgrupos e **desmarque o total**, senão há dupla contagem.

Quando uma combinação de filtros não retorna registros, o painel exibe "Sem dados para o filtro" em vez de um gráfico quebrado.

### 11.6 Conexão com o banco e decisões técnicas

- A URL de conexão vem de `st.secrets["db_url"]`; **nenhuma credencial está no código**.
- `@st.cache_resource` mantém um único *engine* SQLAlchemy, com `pool_pre_ping=True` para reconectar caso o Aiven derrube uma conexão ociosa.
- `@st.cache_data(ttl=60)` guarda cada resultado por até 60 s: mudanças no banco aparecem em até 1 minuto e interações repetidas não sobrecarregam o banco.
- Todas as consultas usam **parâmetros nomeados** (`:i`, `:f`, `:uf`…), sem concatenar entrada do usuário no SQL.
- A agregação é feita **no banco** (`GROUP BY`); o Streamlit apenas desenha os resultados.
- Os índices criados na carga (`ix_acid_ano_uf`, `ix_acid_pessoa`, `ix_mgdi_ano_uf`) aceleram os filtros de ano/UF e as contagens distintas.
- Os óbitos da PRF são contados pelo `estado_fisico` e os acidentes por `COUNT(DISTINCT id)`, pois a base está no nível pessoa (uma linha por envolvido).
- O gráfico 2 usa **taxa por 100 mil habitantes** (e não contagem) para comparar faixas etárias de tamanhos diferentes.

---

## 12. Análise Crítica: ODS 5 e ODS 18

### 12.1 Principais achados

> Valores lidos no dashboard publicado com os filtros padrão: **período 2021–2025**, todas as UFs, todos os sexos e faixas etárias, e o grupo CID-10 "Acidentes de transporte". Os valores dos cartões são exatos; os lidos diretamente dos gráficos são aproximados (os números exatos estão no expansor **"Ver dados consultados"**).

- **Dimensão do problema** (cartão 1): o SIM registra **182.069 óbitos** no trânsito entre 2021 e 2025.
- **ODS 5, composição por sexo** (cartão 2 e gráfico 1): as mulheres respondem por **17,2 %** dos óbitos; os homens concentram a grande maioria. Por ano, são cerca de 29 a 31 mil óbitos masculinos contra cerca de 6 mil femininos, com leve alta em 2024 e 2025.
- **ODS 5, risco por faixa etária** (gráfico 2): a maior taxa masculina está na faixa de **20 a 49 anos**, com cerca de **37 óbitos por 100 mil habitantes**, e se mantém entre 35 e 37 por 100 mil nas faixas de 50 a 69 e de 70 anos ou mais. Entre as mulheres, a maior taxa está na faixa de **70 anos ou mais**, com cerca de **9 por 100 mil**. Na faixa de 20 a 49 anos, o risco masculino é cerca de **6 vezes** o feminino; entre 15 e 19 anos, cerca de 4 vezes.
- **ODS 5, recorte territorial** (cartão 4 e gráfico 4): **Minas Gerais (MG)** é a UF com mais óbitos nas rodovias federais (acima de 3,5 mil no período), seguida por **PR, BA, SC e RS**.
- **ODS 18, composição racial** (cartão 3 e gráfico 3): pretos e pardos somam **60,5 %** dos óbitos (com "ignorado" no denominador). A composição é praticamente estável de 2021 a 2025: cerca de 54 % pardos, 38 % brancos e 6 % pretos.
- **ODS 18, qualidade do registro** (gráfico 3): a categoria "ignorado" é muito pequena, da ordem de 1 % a 2 % ao ano, o que indica bom preenchimento de raça/cor no período e dá mais segurança à leitura do indicador.

### 12.2 O que a análise revela

1. **Contagem não é risco.** Comparar apenas o número de óbitos esconde diferenças de população e de largura das faixas etárias. Por isso o gráfico 2 usa taxa por 100 mil habitantes, e é ele que permite afirmar algo sobre o risco por sexo (ODS 5).
2. **Gênero exige duas leituras combinadas.** A composição por sexo (cartão 2 e gráfico 1) mostra *quem são as vítimas*; a taxa por faixa etária (gráfico 2) mostra *quem está mais exposto por habitante*. Juntas, separam a proporção de vítimas do risco individual.
3. **Raça/cor mostra composição, não risco.** O gráfico 3 evidencia o perfil racial das vítimas, mas, sem a população de cada grupo como denominador, ele sozinho não comprova desigualdade de risco (ODS 18). Essa conclusão exigiria comparar o resultado com a participação de cada grupo na população (por exemplo, Censo/IBGE).
4. **A qualidade do registro é, em si, um indicador de equidade.** A fatia "ignorado" do gráfico 3 mostra o quanto a informação de raça/cor deixa de ser preenchida; quanto maior, menos confiável é qualquer leitura racial.
5. **Fontes distintas respondem a perguntas distintas.** O SIM dá o panorama nacional por sexo e raça/cor, o MGDI dá taxas por UF, sexo e faixa etária, e a PRF dá o recorte das rodovias federais. A integração das três é o que permite olhar as duas ODS ao mesmo tempo.
6. **Há armadilhas de dupla contagem.** O grupo "Acidentes de transporte" do SIM já é o total; somá-lo aos subgrupos duplicaria os óbitos. O dashboard parte do total e avisa o usuário ao detalhar.

### 12.3 Limitações e cuidados de interpretação

- **Escopos diferentes entre as fontes.** A PRF cobre apenas **rodovias federais**; SIM e MGDI cobrem o território todo. Os números absolutos **não são comparáveis** entre fontes, e o ranking de UFs (gráfico 4) não representa a mortalidade total do estado.
- **Raça/cor sem recorte territorial.** O SIM utilizado é nacional, então não é possível cruzar raça/cor com UF.
- **"Ignorado" no denominador.** O cartão 3 inclui "ignorado" no total, o que tende a **subestimar** a participação de pretos e pardos quando o preenchimento é ruim.
- **Cobertura temporal distinta.** A PRF cobre 2021–2025 e o MGDI vai até 2024; o filtro de período usa a união dos anos, então algumas fontes podem ter menos anos que outras em um mesmo intervalo.
- **Escopo do grupo "Acidentes de transporte".** Por ser o total da causa no SIM, pode abranger modalidades não rodoviárias, a depender do recorte exportado do TABNET; convém conferir ao interpretar o cartão 1.
- **Associação, não causalidade.** Os dados são agregados e descritivos; não permitem inferir causas.

---

## 13. Execução e Deploy do Dashboard

O dashboard só precisa de um banco PostgreSQL **já carregado** (Aiven ou local) e da URL de conexão em `st.secrets["db_url"]`.

### 13.1 Executar localmente

1. Crie o arquivo `.streamlit/secrets.toml` na raiz do repositório. Ele já está no `.gitignore`, e o Streamlit lê a pasta `.streamlit/` do diretório onde o comando é executado:

```toml
# .streamlit/secrets.toml  (NUNCA versionar)
db_url = "postgresql+psycopg2://avnadmin:SENHA@HOST:PORTA/db_transito_brasil?sslmode=require"
```

   Para o banco local de desenvolvimento, use `postgresql+psycopg2://postgres:SENHA@localhost:5432/db_transito_brasil`.

2. Instale as dependências e execute, em **um comando**:

```bash
pip install -r dashboard/requirements.txt && streamlit run dashboard/app.py
```

O dashboard abre em http://localhost:8501.

### 13.2 Publicar no Streamlit Community Cloud

1. Mantenha este código em um repositório no GitHub (os segredos **não** vão no repositório).
2. Em [share.streamlit.io](https://share.streamlit.io), clique em **New app** e selecione o repositório, a branch `main` e o *Main file path* **`dashboard/app.py`**. As dependências são lidas de `dashboard/requirements.txt`.
3. Em **Advanced settings → Secrets**, cole o conteúdo do `secrets.toml` acima (`db_url = "..."`).
4. Garanta que o Aiven aceita conexões do Streamlit Cloud (o `ip_filter_object` de `infra/aiven/main.tf` já libera os IPs dinâmicos).
5. Clique em **Deploy**. A versão em produção deste projeto está em: https://big-data-project-sbqwmipsjzjwtopxganx2j.streamlit.app/

### 13.3 Provisionar o Aiven e carregar os dados

1. Provisione o serviço com Terraform, conforme a [seção 4](#nuvem-postgresql-gerenciado-no-aiven-infraaiven) e o [`infra/aiven/README.md`](infra/aiven/README.md).
2. Com os CSVs já tratados em `data/versao.resultado/` (etapa de ETL da [seção 6](#6-guia-de-execução-e-reprodução)), aponte o script de carga para o serviço por variáveis de ambiente e execute-o:

```bash
export DB_HOST="<host do serviço>"
export DB_PORT="<porta do serviço>"
export DB_USER="avnadmin"
export DB_PASS="<senha do serviço>"
export DB_NAME="db_transito_brasil"
export PGSSLMODE="require"          # o Aiven exige TLS
python3 scripts/carregar_postgres.py
```

| Variável | Padrão | Observação |
|----------|--------|------------|
| `DB_PASS` | n/d | **Obrigatória** |
| `DB_USER` | `postgres` | No Aiven: `avnadmin` |
| `DB_HOST` | `localhost` | No Aiven: host do serviço |
| `DB_PORT` | `5432` | No Aiven: porta do serviço |
| `DB_NAME` | `db_transito_brasil` | |

> ⚠️ O `service_uri` retornado pelo Terraform aponta, por padrão, para o banco `defaultdb`. Como as tabelas são carregadas em `db_transito_brasil`, **troque o nome do banco no final da URI** ao montar a `db_url` do dashboard.

### 13.4 Segurança

- **Nunca versionar** `terraform.tfvars`, `*.tfstate`, `.streamlit/secrets.toml` nem tokens; todos já estão no `.gitignore`.
- O token do Aiven é passado por `TF_VAR_aiven_api_token` (variável `sensitive`), e a `service_uri` é um *output* `sensitive`.
- O `ip_filter_object` libera `0.0.0.0/0` porque o Streamlit Cloud não possui IP fixo; a proteção fica por conta de TLS e de senha forte. Como melhoria, recomenda-se criar um **usuário somente leitura** no Aiven para o dashboard.

---

## Fontes de Dados

- **DATASUS / TABNET** – Sistema de Informações sobre Mortalidade (SIM): https://datasus.saude.gov.br
- **Polícia Rodoviária Federal (PRF)** – Dados abertos de acidentes: https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos
- **Ministério da Saúde** – Indicadores MGDI de óbitos no trânsito

---

## Licença e Autoria

- **Repositório:** [celesteadoq/big-data-project](https://github.com/celesteadoq/big-data-project)
- **Licença:** _defina aqui a licença do projeto (ex.: MIT)._

Contribuições, sugestões e *issues* são bem-vindas.