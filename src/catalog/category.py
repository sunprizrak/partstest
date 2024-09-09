from abc import ABC, abstractmethod
from src.catalog.part import create_part_instance


class BaseCategory:

    def __init__(self, *args, **kwargs):
        self.catalog = kwargs.get('catalog')
        self.data = kwargs.get('data')
        if kwargs.get('root_id'):
            self.root_id = kwargs.get('root_id')
        self.id = kwargs.get('category_id')
        self.children = []

    def add_children(self, child_id, data, root_id):
        child = create_category_children_instance(child_id=child_id, data=data, root_id=root_id)
        self.children.append(child)
        return child

    def get_children(self):
        response = self.catalog.get_category(category_id=self.id)

        if response.status_code != 200:
            self.catalog.logger.warning(
                f'Bad request {self.catalog.current_url} catalog: {self.catalog.name} category_id: {self.id}')
            return False

        data = response.json().get('data')

        if not data:
            self.catalog.logger.warning(f'Note data in catalog: {self.catalog.name} category_id: {self.id}')
            return False

        for subcategory in data:
            children = subcategory.get('children')

            if not children:
                self.catalog.logger.warning(
                    f'No children in data catalog: {self.catalog.name} category_id: {self.id}')
                continue

            for child_data in children:
                child_id = child_data.get('id')

                kwargs_dict = {
                    'child_id': child_id,
                    'data': data,
                }

                if hasattr(self, 'root_id'):
                    kwargs_dict['root_id'] = self.root_id
                else:
                    kwargs_dict['root_id'] = self.id

                self.add_children(**kwargs_dict)
        return self.children


class Category(ABC, BaseCategory):

    def __init__(self, *args, **kwargs):
        super(Category, self).__init__(*args, *kwargs)
        self.name = kwargs.get('name')
        self.part_lists = []
        self.parts = []
        self.validation_fields = set()
        self.validation_image_fields = set()

    def add_part_lists(self, part_list):
        self.part_lists.extend(part_list)

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


def create_category_instance(catalog, category_id, name, data):
    cls = globals().get(f"{catalog.name.capitalize()}Category")
    if cls is None:
        raise ValueError(f"Class {catalog.name.capitalize()}Category is not defined.")
    return cls(catalog=catalog, category_id=category_id, name=name, data=data)


def create_category_children_instance(child_id, data, root_id):
    return BaseCategory(child_id=child_id, data=data, root_id=root_id)


if __name__ == '__main__':
    pass
