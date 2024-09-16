import time
from abc import ABC, abstractmethod

from progress.bar import IncrementalBar

from src.catalog.part import create_part_instance


class Category(ABC):
    name_label_part = 'name'

    def __init__(self, *args, **kwargs):
        self.catalog = kwargs.get('catalog')
        self.data = kwargs.get('data')
        if kwargs.get('root_id'):
            self.root_id = kwargs.get('root_id')
        self.id = kwargs.get('category_id')
        self.name = kwargs.get('name')
        self.children = []
        self.part_lists = []
        self.parts = []
        self.validation_fields = set()
        self.validation_image_fields = set()

    def add_children(self, child_id, child_name, data, root_id):
        child = create_category_instance(catalog=self.catalog, category_id=child_id, name=child_name, data=data, root_id=root_id)
        self.children.append(child)
        return child

    def add_part_lists(self, part_list):
        self.part_lists.extend(part_list)

    def add_part(self, part_id, name):
        part = create_part_instance(catalog=self.catalog, category=self, part_id=part_id, name=name)
        self.parts.append(part)

    @abstractmethod
    def get_parts(self, test_api):
        bar = IncrementalBar(f'receive PARTS from PARTLISTS {self} ', max=len(self.part_lists), suffix='%(index)d/%(max)d ')
        for part_list in self.part_lists:
            if test_api:
                time.sleep(0.2)

            response = self.catalog.get_parts(child_id=part_list.id)

            if response.status_code != 200:
                self.catalog.logger.warning(
                    f'Bad request {self.catalog.current_url} {self.catalog}/{self}/{part_list} ')
                continue

            data = response.json().get('data')

            if not data:
                self.catalog.logger.warning(
                    f'No Parts in {self.catalog}/{self}/{part_list}')
                continue

            if test_api:
                data = data[:1]

            for part in data:
                part_id = part.get('id')
                part_name = part.get(self.name_label_part)
                self.add_part(part_id=part_id, name=part_name)
            bar.next()
        bar.finish()

    @abstractmethod
    def get_children(self, test_api, part_list):
        response = self.catalog.get_category(category_id=self.id)

        if response.status_code != 200:
            self.catalog.logger.warning(
                f'Bad request {self.catalog.current_url} {self.catalog}/{self}')
            return False

        data = response.json().get('data')

        if not data:
            self.catalog.logger.warning(
                f'Note data in {self.catalog}/{self}')
            return False

        if test_api:
            data = data[:1]

        for subcategory in data:
            if part_list:
                children = data
            else:
                children = subcategory.get('children')

            if not children:
                self.catalog.logger.warning(
                    f'No children in data {self.catalog}/{self}')
                continue

            if test_api:
                children = children[:1]

            for child_data in children:
                child_id = child_data.get('id')
                child_name = child_data.get(self.catalog.name_label_category)

                kwargs_dict = {
                    'child_id': child_id,
                    'child_name': child_name,
                    'data': child_data,
                }

                if hasattr(self, 'root_id'):
                    kwargs_dict['root_id'] = self.root_id
                else:
                    kwargs_dict['root_id'] = self.id

                self.add_children(**kwargs_dict)
        return self.children

    @abstractmethod
    def validate(self, data: dict):
        image_fields = data.get('imageFields')

        missing_fields = self.validation_fields - data.keys()

        if len(missing_fields) > 0:
            self.catalog.logger.warning(
                f"Missing fields {missing_fields} in {self.catalog}/{self}")

        if image_fields:
            missing_fields = self.validation_image_fields - image_fields.keys()

            if len(missing_fields) > 0:
                self.catalog.logger.warning(
                    f"Missing fields  {missing_fields} in imageFields => in {self.catalog}/{self}")

    def __str__(self):
        return f"{self.name} id:{self.id}"

    def __repr__(self):
        return f"{self.name} id:{self.id}"


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
        return super().validate(data=data)

    def get_children(self, test_api, part_list=None):
        return super().get_children(test_api, part_list)

    def get_parts(self, test_api):
        return super().get_parts(test_api)


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
        return super().validate(data=data)

    def get_children(self, test_api, part_list=None):
        return super().get_children(test_api, part_list)

    def get_parts(self, test_api):
        return super().get_parts(test_api)


class GrimmeCategory(Category):
    def __init__(self, *args, **kwargs):
        super(GrimmeCategory, self).__init__(*args, **kwargs)
        self.modifications = []
        self.validation_fields = {
            'id', 'label', 'parent_id', 'linkType',
            'children', 'created_at', 'updated_at',
        }

    def get_children(self, test_api, part_list=None):
        response = self.catalog.get_category(category_id=self.id)

        if response.status_code != 200:
            self.catalog.logger.warning(
                f'Bad request {self.catalog.current_url} catalog: {self.catalog.name} category_name: {self.name} category_id: {self.id}')
            return False

        children = response.json().get('data')

        if not children:
            self.catalog.logger.warning(
                f'No children in data catalog: {self.catalog.name} category_name: {self.name} category_id: {self.id}')
            return False

        if test_api:
            children = children[:1]

        for child_data in children:
            child_id = child_data.get('id')
            child_name = child_data.get(self.catalog.name_label_category)

            kwargs_dict = {
                'child_id': child_id,
                'child_name': child_name,
                'data': child_data,
            }

            if hasattr(self, 'root_id'):
                kwargs_dict['root_id'] = self.root_id
            else:
                kwargs_dict['root_id'] = self.id

            self.add_children(**kwargs_dict)
        return self.children

    def get_parts(self, test_api):
        bar = IncrementalBar(
            messege=f'receive PARTS from PARTLISTS {self.name} ',
            max=len(self.part_lists),
            suffix='%(index)d/%(max)d ',
        )
        for part_list in self.part_lists:
            bar.next()

            if test_api:
                time.sleep(0.2)

            response = self.catalog.get_category(category_id=part_list.id)

            if response.status_code != 200:
                self.catalog.logger.warning(
                    f'Bad request {self.catalog.current_url} catalog: {self.catalog.name} category_name: {self.name} category_id: {self.id} part_list_id: {part_list.id} ')
                continue

            data = response.json().get('data')

            if not data:
                self.catalog.logger.warning(
                    f'No Parts in {self.catalog.name} category_name: {self.name} category_id: {self.id} part_list_id: {part_list.id}')
                continue

            if test_api:
                data = data[:1]

            for part in data:
                part_id = part.get('id')
                part_name = part.get(self.name_label_part)
                self.add_part(part_id=part_id, name=part_name)
        bar.finish()

    def validate(self, data: dict):
        return super().validate(data=data)


class KroneCategory(Category):

    def __init__(self, *args, **kwargs):
        super(KroneCategory, self).__init__(*args, **kwargs)
        self.validation_fields = {
            'id', 'label', 'parent_id', 'linkType',
            'children', 'created_at', 'updated_at',
        }

    def validate(self, data: dict):
        return super().validate(data=data)

    def get_children(self, test_api, part_list=None):
        return super().get_children(test_api, part_list)

    def get_parts(self, test_api):
        return super().get_parts(test_api)


class KvernelandCategory(Category):
    def __init__(self, *args, **kwargs):
        super(KvernelandCategory, self).__init__(*args, **kwargs)
        self.validation_fields = {
            'id', 'label', 'parent_id', 'linkType',
            'children', 'created_at', 'updated_at',
        }

    def validate(self, data: dict):
        return super().validate(data=data)

    def get_parts(self, test_api):
        return super().get_parts(test_api)

    def get_children(self, test_api, part_list=None):
        return super().get_children(test_api, part_list)


class JdeereCategory(Category):

    def __init__(self, *args, **kwargs):
        super(JdeereCategory, self).__init__(*args, **kwargs)
        self.validation_fields = {
            'id', 'label', 'parent_id', 'linkType',
            'children', 'created_at', 'updated_at',
        }

    def validate(self, data: dict):
        return super().validate(data=data)

    def get_parts(self, test_api):
        return super().get_parts(test_api)

    def get_children(self, test_api, part_list=None):
        return super().get_children(test_api, part_list)


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
        return super().validate(data=data)

    def get_children(self, test_api, part_list=None):
        return super().get_children(test_api, part_list)

    def get_parts(self, test_api):
        return super().get_parts(test_api)


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
        return super().validate(data=data)

    def get_children(self, test_api, part_list=None):
        return super().get_children(test_api, part_list)

    def get_parts(self, test_api):
        return super().get_parts(test_api)


def create_category_instance(catalog, category_id, name, data, root_id=None):
    cls = globals().get(f"{catalog.name.capitalize()}Category")
    cleaned_name = name.strip().replace('\n', '')
    if cls is None:
        raise ValueError(f"Class {catalog.name.capitalize()}Category is not defined.")

    if root_id:
        return cls(catalog=catalog, category_id=category_id, name=cleaned_name, data=data, root_id=root_id)
    else:
        return cls(catalog=catalog, category_id=category_id, name=cleaned_name, data=data)


if __name__ == '__main__':
    pass
