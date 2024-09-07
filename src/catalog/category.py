from abc import ABC, abstractmethod
from src.catalog.part import create_part_instance


class Category(ABC):

    def __init__(self, *args, **kwargs):
        self.catalog = kwargs.get('catalog')
        self.id = kwargs.get('category_id')
        self.name = kwargs.get('name')
        self.parts = []
        self.validation_fields = set()
        self.validation_image_fields = set()

    def add_part(self, part_id):
        part = create_part_instance(catalog=self.catalog, category=self, part_id=part_id)
        self.parts.append(part)

    @abstractmethod
    def validate(self, data: dict):
        pass

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class LemkenCategory(Category):

    def __init__(self, *args, **kwargs):
        super(LemkenCategory, self).__init__(*args, **kwargs)
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

    def __init__(self, *args, **kwargs):
        super(KubotaCategory, self).__init__(*args, **kwargs)
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


class GrimmeCategory(Category):
    def __init__(self, *args, **kwargs):
        super(GrimmeCategory, self).__init__(*args, **kwargs)
        self.modifications = []
        self.validation_fields = {
            'id', 'label', 'parent_id', 'linkType',
            'children', 'created_at', 'updated_at',
        }

    def validate(self, data: dict):
        missing_fields = self.validation_fields - data.keys()

        if len(missing_fields) > 0:
            self.catalog.logger.warning(
                f"Missing fields {missing_fields} in catalog: {self.catalog.name} category_id: {self.id}")


class KroneCategory(Category):

    def __init__(self, *args, **kwargs):
        super(KroneCategory, self).__init__(*args, **kwargs)
        self.validation_fields = {
            'id', 'label', 'parent_id', 'linkType',
            'children', 'created_at', 'updated_at',
        }

    def validate(self, data: dict):
        pass


class KvernelandCategory(Category):
    def __init__(self, *args, **kwargs):
        super(KvernelandCategory, self).__init__(*args, **kwargs)
        self.validation_fields = {
            'id', 'label', 'parent_id', 'linkType',
            'children', 'created_at', 'updated_at',
        }

    def validate(self, data: dict):
        pass


class JdeereCategory(Category):

    def __init__(self, *args, **kwargs):
        super(JdeereCategory, self).__init__(*args, **kwargs)
        self.validation_fields = {
            'id', 'label', 'parent_id', 'linkType',
            'children', 'created_at', 'updated_at',
        }

    def validate(self, data: dict):
        pass


class ClaasCategory(Category):

    def __init__(self, *args, **kwargs):
        super(ClaasCategory, self).__init__(*args, **kwargs)
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


class RopaCategory(Category):
    def __init__(self, *args, **kwargs):
        super(RopaCategory, self).__init__(*args, **kwargs)
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


def create_category_instance(catalog, category_id, name):
    cls = globals().get(f"{catalog.name.capitalize()}Category")
    if cls is None:
        raise ValueError(f"Class {catalog.name.capitalize()}Category is not defined.")
    return cls(catalog=catalog, category_id=category_id, name=name)


if __name__ == '__main__':
    pass
