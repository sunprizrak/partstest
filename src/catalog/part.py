from abc import ABC, abstractmethod


class Part(ABC):

    def __init__(self, part_id):
        self.id = part_id
        self.validation_fields = set()
        self.validation_image_fields = set()

    @abstractmethod
    def validate(self, data: dict):
        pass


class LemkenPart(Part):
    pass

    def validate(self, data: dict):
        pass