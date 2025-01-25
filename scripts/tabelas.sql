CREATE TABLE proposicao (
    ID INTEGER IDENTITY(1,1) PRIMARY KEY ,
    AUTOR VARCHAR(100),
    DATA_PRESENTACAO DATETIME,
    EMENTA NVARCHAR(MAX),
    REGIME VARCHAR(50),
    SITUACCAO VARCHAR(80),
    TIPO_PROPOSICAO VARCHAR(100),
    NUMERO VARCHAR(40) UNIQUE,
    ANO INTEGER,
    CIDADE VARCHAR(60),
    ESTADO VARCHAR(80)
);



SELECT * FROM [dbo].[proposicao];

TRUNCATE table proposicao


DROP TABLE proposicao;

DELETE 
FROM proposicao;

CREATE TABLE tramitacao(
    ID INTEGER IDENTITY(1,1) PRIMARY KEY,
    DATA_CRIACAO TIMESTAMP,
    DESCRICAO VARCHAR(MAX),
    LOCAL_PROPOSICAO VARCHAR(60),
    ID_PROPOSICAO VARCHAR(40),
    FOREIGN KEY (ID_PROPOSICAO) REFERENCES proposicao(NUMERO)
 
);

===== LOGS =======================




-- Info de log ERRO, SUCESS, INFO
CREATE TABLE log_dag(
    ID INTEGER IDENTITY(1, 1) PRIMARY KEY ,
    TIPO_LOG VARCHAR(20),
    MENSAGEM_LOG VARCHAR(150) ,
    JSON_XML VARCHAR(MAX),
    DATA_REGISTRO DATETIME DEFAULT GETDATE()


);

-- Registo de erro

CREATE TABLE dag_error (
    ID INTEGER IDENTITY(1, 1) PRIMARY KEY ,
    NUMERO VARCHAR(40) UNIQUE,
    JSON_XML VARCHAR(MAX),
    MENSAGEM_ERRO VARCHAR(80),
    DATA_REGISTRO DATETIME DEFAULT GETDATE(),
    DATA_ATUALIZACAO DATETIME
)



SELECT * FROM  LOG_DAG;

DELETE FROM log_dag;