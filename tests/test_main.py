import pytest
from src.main import Catalog


catalog_names = ['kubota']    # 'grimme'

for catalog_name in catalog_names:
    Catalog(name=catalog_name)


@pytest.mark.parametrize('catalog', Catalog.objects)
class TestCatalog:

    def test_tree(self, catalog):
        response = catalog.get_tree()
        assert response.status_code == 200

    def test_category(self, catalog):
        for category in catalog.categories:
            response = catalog.get_category(category_id=category.id)
            assert response.status_code == 200

    def test_part(self, catalog):
        for category in catalog.categories:
            for part_id in category.parts:
                response = catalog.get_part(part_id=part_id)
                assert response.status_code == 200







