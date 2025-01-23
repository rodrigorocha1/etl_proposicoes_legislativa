from abc import ABC, abstractmethod


class IOperacoesBanco(ABC):

    @abstractmethod
    def realizar_operacao_banco(self, consulta: str):
        """Método para realizar operações no banco
o
        Args:
            consulta (str): _description_
        """
        pass
