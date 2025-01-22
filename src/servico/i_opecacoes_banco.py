from abc import ABC, abstractmethod


class IOperacoesBanco(ABC):

    @abstractmethod
    def realizar_operacoes_banco(self, consulta: str):
        """Método para realizar operações no banco

        Args:
            consulta (str): _description_
        """
        pass
