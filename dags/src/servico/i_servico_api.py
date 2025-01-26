from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, Generator


class IServicoAPI(ABC):

    @abstractmethod
    def obter_proposicoes(self, numero: Optional[str] = None) -> Generator[Tuple[Dict, str], None, None]:
        pass
