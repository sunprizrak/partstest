import pytest
from src.main import Catalog, Category

catalog_names = ['kubota']    # 'grimme'

for catalog_name in catalog_names:
    Catalog(name=catalog_name)


@pytest.mark.parametrize('catalog', Catalog.objects)
class TestCatalog:

    @pytest.mark.dependency(name="test_tree")
    def test_tree(self, catalog):
        response = catalog.get_tree()

        if response.status_code == 200:
            categories = response.json().get('data')
            if categories:
                for category in categories:
                    category_id = category.get('id')
                    obj = Category(category_id=category_id)
                    catalog.categories.append(obj)
            else:
                assert categories, 'Note Categories'
        else:
            assert response.status_code == 200, f'Bad request {response.status_code}'

    @pytest.mark.dependency(depends=["test_tree"])
    def test_category(self, catalog):
        for category in catalog.categories:
            response = catalog.get_category(category_id=category.id)

            if response.status_code == 200:
                data = response.json().get('data')
                if data:
                    for el in data:
                        children = el.get('children')
                        if children:
                            for part_list in children:
                                external_id = part_list.get('external_id')
                                category.parts_list.append(external_id)

                                response = catalog.get_parts(external_id=external_id)

                                if response.status_code == 200:
                                    data = response.json().get('data')

                                    if data:
                                        for part in data:
                                            part_id = part.get('id')
                                            category.parts.append(part_id)
                                    else:
                                        assert data, 'Note Part List Data'
                                else:
                                    assert response.status_code == 200, f'Bad request {response.status_code}'

                        else:
                            assert children, 'No children(Parts list) in category data'
                else:
                    assert data, 'Note Category Data'

            else:
                assert response.status_code == 200, f'Bad request {response.status_code}'

    @pytest.mark.dependency(depends=["test_category"])
    def test_part(self, catalog):
        for category in catalog.categories:
            for part_id in category.parts:
                response = catalog.get_part(part_id=part_id)

                if response.status_code == 200:
                    pass
                else:
                    assert response.status_code == 200, f'Bad request {response.status_code}'







