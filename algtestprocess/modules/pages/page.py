from abc import ABC, abstractmethod
from typing import Optional


class Page(ABC):
    """Page base class"""

    @abstractmethod
    def run(self, output_path: Optional[str], notebook: bool):
        pass
