def __insercao_regisro(
            self,
            sql: str,
            parametros_sql_consulta: Dict[str, Any],
            colunas: str,
            dados: Dict[str, Any],
            tabela: str,
            proposicao: Dict[str, Any],
            url: str,
            numero: str,
            flag: bool = True,

    ):
        """_summary_

        Args:
            sql (str): Consulta sql 
            parametros_sql_consulta (Dict[str, Any]): parametros da consulta 
            colunas (str): colunas da tabela
            dados (Dict[str, Any]): dados que vai ser enviado a tabela
            tabela (str): nome da tabela
            proposicao (Dict[str, Any]): requisição da api
            url (str): url da api
            numero (str): numero da proposicao
            flag (bool, optional): flag de inserção . Defaults to True.
        """
        try:
            if self.__operacoes_banco.consultar_banco_id(sql=sql, parametros=parametros_sql_consulta) is None or flag:
                placeholders = ", ".join(
                    [f"%({coluna})s" for coluna in dados.keys()])
                sql_banco = f"""
                            INSERT INTO {tabela} ({colunas})
                            VALUES ({placeholders})
                        """

            else:
                campos = ', '.join(
                    [f'{coluna} = %({coluna})s' for coluna in dados.keys()])

                sql_banco = f"""
                            UPDATE {tabela}
                            SET {campos}
                            WHERE NUMERO = {numero}
                        """

            self.__operacoes_banco.realizar_operacao_banco(
                consulta=sql_banco, parametros=dados)

        except KeyError as msg:

            mensagem_erro = f'Não encontrou a chave KeyError: {msg}'
            self.__registrar_erro(
                json_xml=proposicao,
                numero=numero,
                data_registro=self.__obter_data_registro(),
                mensagem_erro=mensagem_erro,
                url_api=url
            )

        except IntegrityError as msg:

            mensagem_erro = f'Já existe a chave, {numero}'
            self.__registrar_log(
                json_xml=proposicao,
                mensagem_log=mensagem_erro,
                url_api=url
            )

        except DatabaseError as msg:

            # mensagem_erro = f'Dados invalidos em {str(msg.args[1]).split(', ')[1]}'
            mensagem_erro = f'Erro ao executar operação: {msg}'
            self.__registrar_erro(
                json_xml=proposicao,
                numero=numero,
                data_registro=self.__obter_data_registro(),
                mensagem_erro=mensagem_erro,
                url_api=url)

        except Exception as msg:

            mensagem_erro = f'Erro fatal: {msg}'
            self.__registrar_erro(
                json_xml=proposicao,
                numero=numero,
                data_registro=self.__obter_data_registro(),
                mensagem_erro=mensagem_erro,
                url_api=url
            )