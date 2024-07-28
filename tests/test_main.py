import pytest
from src.main import Catalog


catalogs = ['kubota',]    # 'grimme'

for catalog_name in catalogs:
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









