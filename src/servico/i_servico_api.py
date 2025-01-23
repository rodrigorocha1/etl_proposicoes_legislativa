from abc import ABC, abstractmethod
from typing import Any, Dict, Generator


class IServicoAPI(ABC):

    @abstractmethod
    def obter_proposicoes(self) -> Generator[Dict[str, Any], None, None]:
        pass
