from abc import ABC, abstractmethod


class Page(ABC):
    """Page base class"""

    @abstractmethod
    def run(self, output_path: str):
        pass
