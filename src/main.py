import requests


class Catalog:
    api_url = 'http://api.catalog.detalum.ru/api/v1'
    objects = []

    def __init__(self, name):
        self.name = name
        self.categories = []
        self.objects.append(self)

    def get_tree(self):
        resp = requests.get(
            f"{self.api_url}/{self.name}/catalog/tree"
        )
        return resp

    def get_category(self, category_id):
        resp = requests.get(
            f"{self.api_url}/{self.name}/catalog/{category_id}"
        )
        return resp

    def get_parts(self, external_id):
        resp = requests.get(
            f"{self.api_url}/{self.name}/catalog/{external_id}/parts"
        )
        return resp

    def get_part(self, part_id):
        resp = requests.get(
            f"{self.api_url}/{self.name}/part/{part_id}"
        )
        return resp


class Category:

    def __init__(self, category_id):
        self.id = category_id
        self.parts_list = []
        self.parts = []


if __name__ == '__main__':
    catalog = Catalog(name='claas')
    response = catalog.get_parts(external_id='Зерноуборочные_комбайны/LEXION/LEXION 8900-8600 GEN 1 (C86)')
    print(response.json().get('message'))
    # data = response.json().get('data')
    # for el in data[0]:
    #     print(el)
    # response = catalog.get_part(part_id=251166)
    # for key, val in response.json().items():
    #     print(f'{key}: {val}')


