import requests


class Catalog:
    api_url = 'http://api.catalog.detalum.ru/api/v1'
    objects = []

    def __init__(self, name):
        self.name = name
        self.categories = []
        self.parts_ids = []
        self.objects.append(self)

    def get_tree(self):
        resp = requests.get(
            f"{self.api_url}/{self.name}/catalog/tree"
        )

        if resp.status_code == 200:
            categories = resp.json().get('data')
            for category in categories:
                category_id = category.get('id')
                obj = Category(category_id=category_id)
                self.categories.append(obj)

        return resp

    def get_category(self, category_id):
        resp = requests.get(
            f"{self.api_url}/{self.name}/catalog/{category_id}"
        )

        return resp

    def get_parts(self, category_id):
        resp = requests.get(
            f"{self.api_url}/{self.name}/catalog/{category_id}/parts"
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
        self.parts = []


if __name__ == '__main__':
    catalog = Catalog(name='kubota')
    catalog.get_tree()
    response = catalog.get_parts(category_id=catalog.categories[0].id)
    # data = response.json().get('data')
    # for el in data:
    #     print(el)
    for key, value in response.json().items():
        print(f"{key}: {value}")
        print('-----------------------------------------------------------------------')



