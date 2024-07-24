from abc import ABC, abstractmethod


class DatabaseModel(ABC):
    
    @abstractmethod
    def create(self, data):
        pass
    
    @abstractmethod
    def update(self, id, data):
        pass
    
    @abstractmethod
    def get(self, id):
        pass
