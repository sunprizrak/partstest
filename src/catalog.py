import requests


class Catalog:
    api_url = 'http://api.catalog.detalum.ru/api/v1'

    def __init__(self, name):
        self.name = name
        self.current_url = None
        self.categories = []
        self.parts = []
        self.logger = None

    def add_category(self, category_id):
        obj = Category(category_id=category_id)
        self.categories.append(obj)

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


class Category:

    def __init__(self, category_id):
        self.id = category_id

    def __repr__(self):
        return str(self.id)


if __name__ == '__main__':
    catalog = Catalog(name='claas')
    response = catalog.get_tree()
    data = response.json().get('data')
    children = data[0].get('children')
    for el in children:
        for key, val in el.items():
            print(f'{key}: {val}')
        print('------------------------')

    response = catalog.get_parts(child_id=400)
    print(response.json())



