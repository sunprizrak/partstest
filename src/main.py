import requests


class Catalog:
    api_url = 'http://api.catalog.detalum.ru/api/v1'

    def __init__(self, name):
        self.name = name
        self.current_url = None
        self.categories = []
        self.parts = []

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


class Category:

    def __init__(self, category_id):
        self.id = category_id


if __name__ == '__main__':
    catalog = Catalog(name='lemken')
    response = catalog.get_parts(child_id=173900)
    data = response.json().get('data')
    print(data)
    # print(len(data))
    # for el in data:
    #     print(el.get('id'))
    # response = catalog.get_category(category_or_children_id=173898)
    # data = response.json().get('data')
    # print(type(data))
    #
    # for el in data:
    #     print(el.get('children'))
    # for el in data:
    #     children = el.get('children')
    #     for el in children:
    #         print(el)
    # response = catalog.get_part(part_id=251166)
    # for key, val in response.json().items():
    #     print(f'{key}: {val}')


