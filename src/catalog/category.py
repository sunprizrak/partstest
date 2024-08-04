from abc import ABC, abstractmethod

from progress.bar import IncrementalBar


class Category(ABC):

    def __init__(self, catalog,  category_id):
        self.catalog = catalog
        self.id = category_id
        self.subcategories = []
        self.parts = []
        self.validation_fields = set()
        self.validation_image_fields = set()

    @abstractmethod
    def validate(self, data: dict):
        pass

    @abstractmethod
    def get_parts(self):
        pass


class LemkenCategory(Category):

    def __init__(self, catalog, category_id):
        super(LemkenCategory, self).__init__(catalog, category_id)
        self.parts_list = []
        self.validation_fields = {
            'id', 'name', 'parent_id', 'link_type', 'children',
            'created_at', 'updated_at', 'position', 'description',
            'remark', 'imageFields',
        }
        self.validation_image_fields = {'name', 's3'}

    def validate(self, data: dict):
        if data:
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

    def __get_parts_list(self):
        bar = IncrementalBar(f'receive parts list', max=len(self.subcategories), suffix='%(index)d/%(max)d ')
        for children_id in self.subcategories:
            bar.next()
            response = self.catalog.get_category(category_or_children_id=children_id)

            if response.status_code != 200:
                self.catalog.logger.warning(
                    f'Bad request catalog: {self.catalog.name} category_id: {self.id} children_id: {children_id} {self.catalog.current_url}')
                continue

            data = response.json().get('data')

            if not data:
                self.catalog.logger.warning(f'No data in catalog: {self.catalog.name} category_id: {self.id} children_id: {children_id}')
                continue

            for el in data:
                children = el.get('children')

                if not children:
                    self.catalog.logger.warning(
                        f'No children in data catalog: {self.catalog.name} category_id: {self.id} children_id: {children_id}')
                    continue

                for child in children:
                    child_id = child.get('id')
                    self.parts_list.append(child_id)
        bar.finish()

    def get_parts(self):
        self.__get_parts_list()
        bar = IncrementalBar(f'receive parts from parts list', max=len(self.parts_list),suffix='%(index)d/%(max)d ')
        for part_list_id in self.parts_list[1:3]:
            bar.next()
            response = self.catalog.get_parts(child_id=part_list_id)

            if response.status_code != 200:
                self.catalog.logger.warning(
                    f'Bad request catalog: {self.catalog.name} category_id: {self.id} part_list_id: {part_list_id} {self.catalog.current_url}')
                continue

            data = response.json().get('data')

            if not data:
                self.catalog.logger.warning(f'No Parts in {self.catalog.name} category_id: {self.id} part_list_id: {part_list_id}')
                continue

            for part in data:
                part_id = part.get('id')
                self.parts.append(part_id)

        bar.finish()




class KubotaCategory(Category):

    def __init__(self, catalog, category_id):
        super(KubotaCategory, self).__init__(catalog, category_id)
        self.validation_fields = {
            'id', 'name', 'part_number', 'entity',
            'link_type', 'parent_id', 'children',
        }

    def validate(self, data: dict):
        if data:
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
        if data:
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
        if data:
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
