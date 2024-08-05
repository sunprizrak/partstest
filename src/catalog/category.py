from abc import ABC, abstractmethod
from .part import create_part_instance


class Category(ABC):

    def __init__(self, catalog,  category_id):
        self.catalog = catalog
        self.id = category_id
        self.parts = []
        self.validation_fields = set()
        self.validation_image_fields = set()

    def add_part(self, part_id):
        part = create_part_instance(catalog=self.catalog, category=self, part_id=part_id)
        self.parts.append(part)

    @abstractmethod
    def validate(self, data: dict):
        pass


class LemkenCategory(Category):

    def __init__(self, catalog, category_id):
        super(LemkenCategory, self).__init__(catalog, category_id)
        self.validation_fields = {
            'id', 'name', 'parent_id', 'link_type', 'children',
            'created_at', 'updated_at', 'position', 'description',
            'remark', 'imageFields',
        }
        self.validation_image_fields = {'name', 's3'}

    def validate(self, data: dict):
        image_fields = data.get('imageFields')

        missing_fields = self.validation_fields - data.keys()

        if len(missing_fields) > 0:
            self.catalog.logger.warning(
                f"Missing fields {missing_fields} in catalog: {self.catalog.name} category_id: {self.id}")

        if image_fields:
            missing_fields = self.validation_image_fields - image_fields.keys()

            if len(missing_fields) > 0:
                self.catalog.logger.warning(
                    f"Missing fields  {missing_fields} in imageFields => in catalog: {self.catalog.name} category_id: {self.id}")


class KubotaCategory(Category):

    def __init__(self, catalog, category_id):
        super(KubotaCategory, self).__init__(catalog, category_id)
        self.validation_fields = {
            'id', 'name', 'part_number', 'entity',
            'link_type', 'parent_id', 'children',
        }

    def validate(self, data: dict):
        missing_fields = self.validation_fields - data.keys()

        if len(missing_fields) > 0:
            self.catalog.logger.warning(
                f"Missing fields {missing_fields} in catalog: {self.catalog.name} category_id: {self.id}")


class GrimmeCategory(Category):
    def __init__(self, catalog, category_id):
        super(GrimmeCategory, self).__init__(catalog, category_id)
        self.validation_fields = {
            'id', 'label', 'parent_id', 'linkType',
            'children', 'created_at', 'updated_at',
        }

    def validate(self, data: dict):
        missing_fields = self.validation_fields - data.keys()

        if len(missing_fields) > 0:
            self.catalog.logger.warning(
                f"Missing fields {missing_fields} in catalog: {self.catalog.name} category_id: {self.id}")


class ClaasCategory(Category):

    def __init__(self, catalog, category_id):
        super(ClaasCategory, self).__init__(catalog, category_id)
        self.validation_fields = {
            'id', 'name', 'parent_id', 'link_type',
            'children', 'created_at', 'updated_at',
            'depth',
        }

    def validate(self, data: dict):
        missing_fields = self.validation_fields - data.keys()

        if len(missing_fields) > 0:
            self.catalog.logger.warning(
                f"Missing fields {missing_fields} in catalog: {self.catalog.name} category_id: {self.id}")


def create_category_instance(catalog, category_id):
    cls = globals().get(f"{catalog.name.capitalize()}Category")
    if cls is None:
        raise ValueError(f"Class {catalog.name.capitalize()}Category is not defined.")
    return cls(catalog, category_id)


if __name__ == '__main__':
    pass
