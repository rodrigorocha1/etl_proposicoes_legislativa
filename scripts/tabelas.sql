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

DELETE 
FROM proposicao

CREATE TABLE tramitacao(
    ID INTEGER IDENTITY(1,1) PRIMARY KEY,
    DATA_CRIACAO TIMESTAMP,
    DESCRICAO VARCHAR(MAX),
    LOCAL_PROPOSICAO VARCHAR(60),
    ID_PROPOSICAO VARCHAR(40),
    FOREIGN KEY (ID_PROPOSICAO) REFERENCES proposicao(NUMERO)
 
);

CREATE TABLE controle_log (
    ID INTEGER IDENTITY(1, 1) PRIMARY KEY ,
    TIPO_LOG VARCHAR(20)  UNIQUE,
    
    DATA_ERRO DATETIME,
    MENSAGEM_LOG VARCHAR(80)
);


BEGIN TRY
    INSERT INTO controle_log (TIPO_LOG, DATA_ERRO, MENSAGEM_LOG)
    VALUES
    ('1-1', GETDATE(), 'ERRO na verificação da conexão da API');
END TRY

BEGIN CATCH
    UPDATE 
    controle_log
    SET DATA_ERRO = GETDATE()
    WHERE TIPO_LOG = '1-1'

END CATCH



SELECT * FROM [dbo].[controle_log]


CREATE TABLE log_dag(
    ID INTEGER IDENTITY(1, 1) PRIMARY KEY ,
    TIPO_LOG VARCHAR(20),
    MENSAGEM_LOG VARCHAR(150),
    JSON_XML VARCHAR(MAX),
    DATA_REGISTRO DATETIME DEFAULT GETDATE()


);

SELECT*
FROM log_dag;

DELETE
FROM log_dag;

TRUNCATE TABLE log_dag

DROP TABLE  log_dag;

INSERT INTO log_dag (CICLO, TIPO_LOG, MENSAGEM_LOG)
VALUES(1, 'INFO', 'a'),
       (2, 'INFO','a')

DECLARE @valor_atual INT;

SELECT @valor_atual = coalesce(max(CICLO), 0)
from log_dag

PRINT @valor_atual


INSERT INTO proposicao (AUTOR, DATA_PRESENTACAO, EMENTA, REGIME, SITUACCAO, TIPO_PROPOSICAO, NUMERO, ANO, CIDADE, ESTADO)
               VALUES (%(Comissão Trabalho, da Previdência e da Assistência Social)s, %(2024-12-05)s, %(Requer seja formulado voto de congratulações com o Ministério do Trabalhoe Emprego pelos 94 anos de existência, celebrados em 26 de novembro de2024, e por sua dedicação contínua na defesa dos trabalhadores, no apoioaos sindicatos, na mediação das relações laborais com o setor privado esua resistência diante das inúmeras reformas administrativas que visaramenfraquecer as relações de trabalho.)s, %(Votado nas comissões)s, %(Aprovado)s, %(RQN)s, %(9174)s, %(2024)s, %(Belo Horizonte)s, %(Minas Gerais)s)