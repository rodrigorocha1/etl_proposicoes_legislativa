from abc import ABC, abstractmethod
from typing import Dict, Generator


class IServicoAPI(ABC):

    @abstractmethod
    def obter_proposicoes(self) -> Generator[Dict, None, None]:
        pass
