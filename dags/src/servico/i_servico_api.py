from abc import ABC, abstractmethod
from typing import Tuple, Dict, Generator


class IServicoAPI(ABC):

    @abstractmethod
    def obter_proposicoes(self) -> Generator[Tuple[Dict, str], None, None]:
        pass
