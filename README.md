# Projeto: ETL com Apache Airflow usando a API de Dados Abertos da Assembleia Legislativa de Minas

## 1. Introdução

Este projeto tem como objetivo propor uma estrutura de ETL usando Python e Apache Airflow.

## 2. Requisitos Funcionais

### Coleta de dados
O sistema vai coletar dados do endpoint:

- https://dadosabertos.almg.gov.br/ws/proposicoes/pesquisa/direcionada?tp=100&formato=json&ano=2024&ord=3&p=50000&ini=20250123&fim=20250126, utilizando os filtros de paginação, data de início e data de fim.
- https://dadosabertos.almg.gov.br/ws/proposicoes/pesquisa/direcionada?formato=json&ano=2024&num=11063: URL de exemplo para fazer o reprocessamento.

### Processamento de dados
O sistema deverá realizar o tratamento de caracteres, como:
- Remover espaços desnecessários;
- Remover caracteres de quebra de linha, deixando o texto em uma única linha;
- Formatar datas corretamente.

### Armazenamento de dados
Os dados serão armazenados no banco SQL Server.

## 3. Requisitos Não Funcionais

- **Execução**: O sistema deve rodar com um intervalo de um dia para envio de dados.
- **Monitoramento**: O sistema deve incluir logs de execução, registrando históricos e erros para reprocessamento.

## 4. Estrutura do Banco de Dados

### Tabela `proposicao`

```sql
CREATE TABLE proposicao (
    ID INTEGER IDENTITY(1,1) PRIMARY KEY,
    AUTOR NVARCHAR(300),
    DATA_PRESENTACAO DATETIME,
    EMENTA NVARCHAR(MAX),
    REGIME VARCHAR(50),
    SITUACCAO VARCHAR(80),
    TIPO_PROPOSICAO VARCHAR(100),
    NUMERO VARCHAR(40) UNIQUE,
    ANO INTEGER,
    CIDADE VARCHAR(60),
    ESTADO VARCHAR(80),
    DATA_INSERSAO_REGISTRO DATETIME DEFAULT GETDATE(),
    DATA_ATUALIZACAO_REGISTRO DATETIME
);
```
| Campo                         | Tipo        | Descrição                                                       |
|--------------------------------|------------|-----------------------------------------------------------------|
| ID                             | Incremental | ID automático                                                  |
| AUTOR                          | String     | Autor da proposição, ex. "Governador Romeu Zema Neto"          |
| DATA_PRESENTACAO               | Timestamp  | Data de apresentação da proposição, ex. "2022-10-06T00:00:00Z" |
| EMENTA                         | String     | Assunto da proposição, ex. "Encaminha o Projeto de Lei 4008 2022..." |
| REGIME                         | String     | Regime de tramitação da proposição, ex. "Especial"             |
| SITUACCAO                      | String     | Situação atual da proposição, ex. "Publicado"                  |
| TIPO_PROPOSICAO                | String     | Tipo da proposição, ex. "MSG"                                  |
| NUMERO                         | String     | Número da proposição, ex. "300"                                |
| ANO                            | Integer    | Ano da proposição, ex. 2022                                    |
| CIDADE                         | String     | Cidade fixa "Belo Horizonte"                                   |
| ESTADO                         | String     | Estado fixo "Minas Gerais"                                     |
| DATA_INSERSAO                  | DATETIME   | Data de inserção do registro: Padrão: DATA ATUAL              |
| DATA_ATUALIZACAO_REGISTRO      | DATETIME   | Data de atualização do registro                               |


### Tabela `tramitacao`

```sql
CREATE TABLE tramitacao (
    ID INTEGER IDENTITY(1,1) PRIMARY KEY,
    DESCRICAO VARCHAR(MAX),
    LOCAL_PROPOSICAO VARCHAR(60),
    ID_PROPOSICAO VARCHAR(40),
    DATA_CRIACAO_TRAMITACAO DATETIME,
    DATA_CRIACAO_REGISTRO DATETIME DEFAULT GETDATE(),
    DATA_ATUALIZACAO_REGISTRO DATETIME,
    FOREIGN KEY (ID_PROPOSICAO) REFERENCES proposicao(NUMERO)
);
```

| Campo                      | Tipo         | Descrição                                              |
|----------------------------|-------------|--------------------------------------------------------|
| id                         | Incremental | ID automático                                         |
| DATA_CRIACAO_TRAMITACAO    | Timestamp   | Data do registro da tramitação, ex. "2022-10-04T00:00:00Z" |
| DESCRICAO                  | String      | Descrição do histórico da tramitação, ex. "Proposição lida em Plenário.\nPublicada no DL..." |
| LOCAL_PROPOSICAO           | String      | Local da tramitação, ex. "Plenário"                   |
| ID_PROPOSICAO              | ForeignKey  | Chave estrangeira que referencia o ID da proposição   |
| DATA_CRIACAO_REGISTRO      | Timestamp   | Data da inserção do registro                          |
| DATA_ATUALIZACAO_REGISTRO  | Timestamp   | Data atualização registro                             |


### Tabela `log_dag`

```sql
CREATE TABLE log_dag (
    ID INTEGER IDENTITY(1,1) PRIMARY KEY,
    TIPO_ERROR INTEGER,
    TIPO_LOG VARCHAR(20),
    URL_API VARCHAR(MAX),
    MENSAGEM_LOG VARCHAR(300),
    JSON_XML VARCHAR(MAX),
    JSON_ENVIO VARCHAR(MAX),
    DATA_REGISTRO DATETIME DEFAULT GETDATE()
);
```

### Tabela `dag_error`

```sql
CREATE TABLE dag_error (
    ID INTEGER IDENTITY(1,1) PRIMARY KEY,
    TIPO_ERROR INTEGER,
    NUMERO VARCHAR(40),
    URL_API VARCHAR(MAX),
    JSON_XML VARCHAR(MAX),
    JSON_ENVIO VARCHAR(MAX),
    MENSAGEM_ERRO VARCHAR(300),
    DATA_REGISTRO DATETIME DEFAULT GETDATE(),
    DATA_ATUALIZACAO DATETIME
);
```

## 5. Fluxo da DAG
![Diagrama de Atividade](https://raw.githubusercontent.com/rodrigorocha1/etl_proposicoes_legislativa/refs/heads/main/out/diagramas/diagrama_atividade/diagrama_atividade.png)
![DAG](https://github.com/rodrigorocha1/etl_proposicoes_legislativa/blob/main/imagens/Captura%20de%20tela%20de%202025-02-02%2013-06-00.png?raw=true)

A DAG inicia verificando a conexão com o banco de dados e a API. Se ambas estiverem ativas, inicia-se o processo ETL para extração e tratamento de dados. Caso algum registro falhe, ele é gravado na tabela `dag_error` e reprocessado antes da finalização do ETL.

## 6. Diagrama de Classe


A figura abaixo, mostra uma proposta de diagrama de classe, com destaque para a a conexão da API e banco de dados, podendo ser substituído sem prejuízo ao funcionamento do processo de ETL.
![DAG](https://github.com/rodrigorocha1/etl_proposicoes_legislativa/blob/main/out/diagramas/diagrama_uml/diagrama_uml.png?raw=true)


---

