from abc import ABC, abstractmethod

class RAGPort(ABC):

    @abstractmethod
    def retrieve(self):
        pass

    @abstractmethod
    def generate(self):
        pass