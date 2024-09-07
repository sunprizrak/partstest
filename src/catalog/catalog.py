import requests
import os
import logging
from datetime import datetime
from abc import ABC, abstractmethod
from src.catalog.category import create_category_instance, LemkenCategory


class Catalog(ABC):
    api_url = 'http://api.catalog.detalum.ru/api/v1'
    name_label_category = 'name'

    def __init__(self, name):
        self.name = name
        self.categories = dict()
        self.current_url = None
        self.validation_fields = set()
        self.validation_image_fields = set()
        self.logger = self.__setup_logger()

    def add_category(self, data):
        category_id = data.get('id')
        name = data.get(self.name_label_category)
        category = create_category_instance(catalog=self, category_id=category_id, name=name)
        self.categories[category_id] = category
        self.categories[category_id].validate(data=data)

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

    def get_tree(self):
        url = f"{self.api_url}/{self.name}/catalog/tree"
        self.current_url = url
        resp = requests.get(url)
        return resp

    def get_category(self, category_id):
        url = f"{self.api_url}/{self.name}/catalog/{category_id}"
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


class LemkenCatalog(Catalog):
    pass


class KubotaCatalog(Catalog):
    pass


class GrimmeCatalog(Catalog):

    def __init__(self, name):
        super(GrimmeCatalog, self).__init__(name)
        self.name_label_category = 'label'


class ClaasCatalog(Catalog):
    pass


class KroneCatalog(Catalog):
    pass


class KvernelandCatalog(Catalog):
    pass


class JdeereCatalog(Catalog):
    pass


class RopaCatalog(Catalog):
    pass


def create_catalog_instance(catalog_name):
    cls = globals().get(f"{catalog_name.capitalize()}Catalog")
    if cls is None:
        raise ValueError(f"Class {catalog_name.capitalize()}Catalog is not defined.")
    return cls(name=catalog_name)


if __name__ == '__main__':
    catalog = create_catalog_instance(catalog_name='ropa')
    response = catalog.get_tree()
    data = response.json().get('data')
    print('---------Categories------------------------------------------')
    print(f"колличество категорий: {len(data)}")
    print(f'type data : {type(data)}')
    print('---------category[0]-------------------------------------------')
    for key, val in data[0].items():
        print(f"{key}: {val}")

    # print('---------Subcategories-----------------')
    # response = catalog.get_category(category_id=4)
    # data = response.json().get('data')
    # for el in data:
    #     print(el)

    # print('-----------Two_subcategories----------------------------------')
    # response = catalog.get_category(category_id=5)
    # data = response.json().get('data')
    # for key, val in data[1].items():
    #     print(f"{key}: {val}")
    #
    # print('--------------lol------------------')
    # response = catalog.get_category(category_id=3568)
    # data = response.json().get('data')
    # for el in data:
    #     print(el)
    #
    # print('-------------lol[1]---------------------------------------')
    # response = catalog.get_category(category_id=3568)
    # data = response.json().get('data')
    # for key, val in data[1].items():
    #     print(f"{key}: {val}")
    #
    # print('---------Parts------------------')
    # response = catalog.get_parts(child_id=4998)
    # data = response.json().get('data')
    # for el in data:
    #     print(el)




