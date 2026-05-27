from abc import ABC, abstractmethod


class BaseHandler(ABC):

    @abstractmethod
    def export(self, quiz):
        pass

    @abstractmethod
    def import_from_string(self, data_string, creator):
        pass

    @abstractmethod
    def validate(self, data_string):
        pass
