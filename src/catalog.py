import requests
import os
import logging
from datetime import datetime
from abc import ABC, abstractmethod


class Catalog(ABC):
    api_url = 'http://api.catalog.detalum.ru/api/v1'

    def __init__(self):
        self.name = self.__class__.__name__.lower()
        self.categories = []
        self.parts = []
        self.current_url = None
        self.validation_fields = set()
        self.validation_image_fields = set()
        self.logger = self.__setup_logger()

    def add_category(self, category_id):
        self.categories.append(category_id)

    def add_part(self, part_id):
        self.parts.append(part_id)

    def __setup_logger(self):
        logs_dir = os.path.join('logs', self.name)

        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        log_file = os.path.join(logs_dir, f"{self.name}_{datetime.now().strftime("%Y-%m-%d")}.log")

        if os.path.exists(log_file):
            os.remove(log_file)

        logger = logging.getLogger(self.name)
        logger.setLevel(logging.WARNING)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.WARNING)

        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        return logger

    @abstractmethod
    def validate(self, fields: dict):
        pass

    def get_tree(self):
        url = f"{self.api_url}/{self.name}/catalog/tree"
        self.current_url = url
        resp = requests.get(url)
        return resp

    def get_category(self, category_or_children_id):
        url = f"{self.api_url}/{self.name}/catalog/{category_or_children_id}"
        self.current_url = url
        resp = requests.get(url)
        return resp

    def get_parts(self, child_id):
        url = f"{self.api_url}/{self.name}/catalog/{child_id}/parts"
        self.current_url = url
        resp = requests.get(url)
        return resp

    def get_part(self, part_id):
        url = f"{self.api_url}/{self.name}/part/{part_id}"
        self.current_url = url
        resp = requests.get(url)
        return resp

    def __repr__(self):
        return self.name


class Lemken(Catalog):

    def __init__(self):
        super(Lemken, self).__init__()
        self.validation_fields = {
            'id', 'name', 'parent_id', 'link_type', 'children',
            'created_at', 'updated_at', 'position', 'description',
            'remark', 'imageFields',
        }
        self.validation_image_fields = {'name', 's3'}

    def validate(self, data: dict):
        if data:
            category_id = data.get('category_id')
            image_fields = data.get('imageFields')

            missing_fields = self.validation_fields - data.keys()

            if len(missing_fields) > 0:
                self.logger.warning(
                    f"Missing fields {missing_fields} in catalog: {self.name} category_id: {category_id}")

            if image_fields:
                missing_fields = self.validation_image_fields - image_fields.keys()

                if len(missing_fields) > 0:
                    self.logger.warning(
                        f"Missing fields  {missing_fields} in imageFields => in catalog: {self.name} category_id: {category_id}")


class Kubota(Catalog):

    def __init__(self):
        super(Kubota, self).__init__()
        self.validation_fields = {
            'id', 'name', 'part_number', 'entity',
            'link_type', 'parent_id', 'children',
        }

    def validate(self, data: dict):
        if data:
            category_id = data.get('category_id')

            missing_fields = self.validation_fields - data.keys()

            if len(missing_fields) > 0:
                self.logger.warning(
                    f"Missing fields {missing_fields} in catalog: {self.name} category_id: {category_id}")


class Grimme(Catalog):

    def __init__(self):
        super(Grimme, self).__init__()
        self.validation_fields = {
            'id', 'label', 'parent_id', 'linkType',
            'children', 'created_at', 'updated_at',
        }

    def validate(self, data: dict):
        if data:
            category_id = data.get('category_id')

            missing_fields = self.validation_fields - data.keys()

            if len(missing_fields) > 0:
                self.logger.warning(
                    f"Missing fields {missing_fields} in catalog: {self.name} category_id: {category_id}")


class Claas(Catalog):
    def __init__(self):
        super(Claas, self).__init__()
        self.validation_fields = {
            'id', 'name', 'parent_id', 'link_type',
            'children', 'created_at', 'updated_at',
            'depth',
        }

    def validate(self, data: dict):
        if data:
            category_id = data.get('category_id')

            missing_fields = self.validation_fields - data.keys()

            if len(missing_fields) > 0:
                self.logger.warning(
                    f"Missing fields {missing_fields} in catalog: {self.name} category_id: {category_id}")


def create_catalog_instance(catalog_name):
    cls = globals().get(catalog_name.capitalize())
    if cls is None:
        raise ValueError(f"Class {catalog_name} is not defined.")
    return cls()


if __name__ == '__main__':
    catalog = create_catalog_instance(catalog_name='lemken')
    print(catalog.name)



