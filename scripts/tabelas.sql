CREATE TABLE proposicao (
    ID INTEGER IDENTITY(1,1) PRIMARY KEY ,
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


SELECT COUNT(*)

FROM  proposicao


SELECT * 
FROM proposicao
where NUMERO = '59'
order by DATA_INSERSAO_REGISTRO desc;

TRUNCATE table proposicao


DROP TABLE proposicao CASCADE;

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

DROP TABLE tramitacao;

===== LOGS =======================




-- Info de log ERRO, SUCESS, INFO
CREATE TABLE log_dag(
    ID INTEGER IDENTITY(1, 1) PRIMARY KEY ,
    TIPO_LOG VARCHAR(20),
    MENSAGEM_LOG VARCHAR(300) ,
    JSON_XML VARCHAR(MAX),
    DATA_REGISTRO DATETIME DEFAULT GETDATE()


);

-- Registo de erro

CREATE TABLE dag_error (
    ID INTEGER IDENTITY(1, 1) PRIMARY KEY ,
    NUMERO VARCHAR(40),
    JSON_XML VARCHAR(MAX),
    MENSAGEM_ERRO VARCHAR(300),
    DATA_REGISTRO DATETIME DEFAULT GETDATE(),
    DATA_ATUALIZACAO DATETIME
)

SELECT *
FROM dag_error;


DROP TABLE dag_error;
INSERT INTO dag_error (NUMERO, JSON_XML, MENSAGEM_ERRO, DATA_ATUALIZACAO)
VALUES('1', 'TESTE', 'TESTE', GETDATE())

BEGIN
    DECLARE @NUMERO VARCHAR(10), @NUMERO_ERROR VARCHAR(10);

    SET @NUMERO = '1';

  
    SELECT @NUMERO_ERROR = NUMERO
    FROM dag_error
    WHERE NUMERO = @NUMERO;

    
    IF @NUMERO_ERROR IS NULL
        PRINT 1 + @NUMERO_ERROR;
    else

        PRINT '2 '+ @NUMERO_ERROR;
END;


SELECT * 
FROM  LOG_DAG
order by DATA_REGISTRO desc;

DELETE FROM log_dag;
DROP TABLE log_dag;

SELECT 
    name AS NomeDoIndice, 
    type_desc AS TipoDoIndice, 
    is_unique AS IndiceUnico
FROM sys.indexes
WHERE object_id = OBJECT_ID('Clientes');