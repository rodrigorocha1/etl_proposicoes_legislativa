from abc import ABC, abstractmethod
from typing import List


class IServicoAPI(ABC):

    @abstractmethod
    def obter_proposicoes(self) -> List:
        pass
