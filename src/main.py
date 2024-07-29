import requests


class Catalog:
    api_url = 'http://api.catalog.detalum.ru/api/v1'
    objects = []

    def __init__(self, name):
        self.name = name
        self.categories = []
        self.objects.append(self)

    def get_local_category(self, category_id):
        for category in self.categories:
            if category.id == category_id:
                return category

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
    catalog = Catalog(name='lemken')
    catalog.get_tree()
    catalog.get_category(category_id=1)
    print(catalog.categories[0].parts)
    print('--------------------------------------------------------------------------------------------------------------')
    response = catalog.get_part(part_id=catalog.categories[0].parts[0])
    data = response.json().get('data')
    for key, val in data.items():
        print(f"{key}: {val}")


