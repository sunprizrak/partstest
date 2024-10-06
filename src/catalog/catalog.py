import aiohttp
import os
import logging
from datetime import datetime
from abc import ABC, abstractmethod
from src.catalog.category import create_category_instance
import asyncio
from database import add_category as db_add_category


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

    async def add_category(self, data):
        category_id = data.get('id')
        name = data.get(self.name_label_category)
        category = await create_category_instance(catalog=self, category_id=category_id, name=name)
        await db_add_category(category_id=category_id, name=name)
        self.categories[category_id] = category

        return category

    def __setup_logger(self):
        logs_dir = os.path.join('logs', self.name)

        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        log_file = os.path.join(logs_dir, f"{self.name}_{datetime.now().strftime('%Y-%m-%d')}.log")

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

    async def _make_request(self, url, retries=10, delay=2, timeout=60):
        """
        Выполняет асинхронный запрос с повторными попытками в случае таймаута.
        :param url: URL для запроса
        :param retries: Количество попыток
        :param delay: Задержка между попытками (в секундах)
        :param timeout: Время ожидания ответа от сервера
        :return: Ответ от сервера или None
        """
        attempt = 1
        async with aiohttp.ClientSession() as session:
            while attempt <= retries:
                try:
                    async with session.get(url, timeout=timeout) as response:
                        response.raise_for_status()
                        return await response.json()
                except (aiohttp.ClientError, asyncio.TimeoutError) as error:
                    self.logger.warning(f"{self.name} {url} Ошибка при попытке {attempt}/{retries}: {error}")

                    if attempt == retries:
                        self.logger.error(f"{self.name} все попытки исчерпаны. Запрос {url} не выполнен.")
                finally:
                    if attempt < retries:
                        await asyncio.sleep(delay)
                    attempt += 1
        return None

    async def fetch_tree(self):
        url = f"{self.api_url}/{self.name}/catalog/tree"
        self.current_url = url
        resp = await self._make_request(url=url)
        return resp

    async def fetch_category(self, category_id):
        url = f"{self.api_url}/{self.name}/catalog/{category_id}"
        self.current_url = url
        resp = await self._make_request(url=url)
        return resp

    async def fetch_parts(self, part_list_id):
        url = f"{self.api_url}/{self.name}/catalog/{part_list_id}/parts"
        self.current_url = url
        resp = await self._make_request(url=url)
        return resp

    async def fetch_part(self, part_id):
        url = f"{self.api_url}/{self.name}/part/{part_id}"
        self.current_url = url
        resp = await self._make_request(url=url)
        return resp

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"{self.name}"


class LemkenCatalog(Catalog):

    def __init__(self, name):
        super(LemkenCatalog, self).__init__(name)
        self.depth = 2


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
    catalog = create_catalog_instance(catalog_name='lemken')
    # response = asyncio.run(catalog.get_tree())
    # print(response)
    # data = response.get('data')
    # print('---------Categories------------------------------------------')
    # print(f"колличество категорий: {len(data)}")
    # print(f'type data : {type(data)}')
    # print('---------category[0]-------------------------------------------')
    # for key, val in data[0].items():
    #     print(f"{key}: {val}")

    # print('---------Subcategories-----------------')
    # response = catalog.get_category(category_id=657132)
    # data = response.json().get('data')
    # print(f"количество sub {len(data)}")
    # for el in data[:1]:
    #     for key, val in el.items():
    #         print(f"{key}: {val}")

    # print('-----------Two_subcategories----------------------------------')
    # response = catalog.get_category(category_id=12)
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
    print('---------Parts------------------')
    response = asyncio.run(catalog.fetch_parts(child_id=144236))
    print(response)
    data = response.get('data')
    print(data)
    print(f"len data: {len(data)}")
    print('<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>..')
    for el in data:
        print(el)




