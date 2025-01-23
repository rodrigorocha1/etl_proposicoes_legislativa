from abc import ABC, abstractmethod
from typing import Dict, Any


class IOperacoesBanco(ABC):

    @abstractmethod
    def realizar_operacao_banco(self, consulta: str, parametros: Dict[str, Any]):
        """Método para realizar operações no banco
o
        Args:
            consulta (str): _description_
        """
        pass
