import pytest
from src.main import Catalog, Category

catalog_names = ['lemken']


def create_catalogs():
    catalogs = [Catalog(name=catalog_name) for catalog_name in catalog_names]
    return catalogs


@pytest.mark.parametrize('catalog', create_catalogs())
class TestCatalog:

    @pytest.mark.dependency(name="test_tree")
    def test_tree(self, catalog):
        response = catalog.get_tree()

        if response.status_code == 200:
            data = response.json().get('data')
            if data:
                for category in data:
                    validation_fields = set()

                    if catalog.name == 'lemken':
                        validation_fields = {
                            'id', 'name', 'parent_id', 'link_type', 'children',
                            'created_at', 'updated_at', 'position', 'description',
                            'remark', 'imageFields',
                        }

                        validation_image_fields = {'name', 's3'}
                        image_fields = category.get('imageFields')

                        if image_fields:
                            image_missing_fields = validation_image_fields - image_fields.keys()

                            assert not image_missing_fields, f'Missing fields  {image_missing_fields} in imageFields => in {catalog.name}'
                        else:
                            assert image_fields, f'Not Image_fields in {catalog.name}'
                    elif catalog.name == 'grimme':
                        validation_fields = {
                            'id', 'label', 'parent_id', 'linkType',
                            'children', 'created_at', 'updated_at',
                        }
                    elif catalog.name == 'claas':  #depth
                        validation_fields = {
                            'id', 'name', 'parent_id', 'link_type',
                            'children', 'created_at', 'updated_at',
                        }

                    missing_fields = validation_fields - category.keys()

                    assert not missing_fields, f'Missing fields {missing_fields} in {catalog.name}'

                    category_id = category.get('id')
                    obj = Category(category_id=category_id)
                    catalog.categories.append(obj)
            else:
                assert data, f'Note Categories in {catalog.name}'
        else:
            assert response.status_code == 200, f'Bad request {catalog.name}'

    @pytest.mark.dependency(depends=["test_tree"])
    def test_category(self, catalog):
        for category in catalog.categories:
            response = catalog.get_category(category_or_children_id=category.id)

            if response.status_code == 200:
                data = response.json().get('data')
                if data:
                    for el in data:
                        children = el.get('children')

                        if children:
                            for main_child in children:
                                children_id = main_child.get('id')
                                response = catalog.get_category(category_or_children_id=children_id)

                                if response.status_code == 200:
                                    data2 = response.json().get('data')

                                    if data2:
                                        for el2 in data2:
                                            children2 = el2.get('children')

                                            if children2:
                                                for child in children2:
                                                    child_id = child.get('id')
                                                    category.parts_list.append(child_id)

                                                    response = catalog.get_parts(child_id=child_id)

                                                    if response.status_code == 200:
                                                        data3 = response.json().get('data')

                                                        if data3:
                                                            for part in data3:
                                                                part_id = part.get('id')
                                                                category.parts.append(part_id)
                                                        else:
                                                            assert data3, f'Note Parts in {catalog.name} category_id: {category.id} children_id: {children_id} child_id: {child_id}'
                                                    else:
                                                        assert response.status_code == 200, f'Bad request in {catalog.name} category_id: {category.id} child_id_id(part list): {child_id}'
                                            else:
                                                assert children2, f'No children2(Parts list) in {catalog.name} category_id: {category.id} children_id: {children_id}'
                                    else:
                                        assert data2, f'Note Children Data in {catalog.name} category_id: {category.id} children_id: {children_id}'
                        else:
                            assert children, f'No children in {catalog.name} category_id: {category.id} data'
                else:
                    assert data, f'Note Category Data in {catalog.name} category_id: {category.id}'
            else:
                assert response.status_code == 200, f'Bad request {catalog.name} category_id: {category.id}'

    @pytest.mark.dependency(depends=["test_category"])
    def test_part(self, catalog):
        for category in catalog.categories:
            for part_id in category.parts:
                response = catalog.get_part(part_id=part_id)

                if response.status_code == 200:
                    data = response.json().get('data')
                    part_category = response.json().get('category')

                    if data:
                        validation_fields = {
                            'id', 'name', 'link_type', 'quantity',
                            'part_number', 'position', 'dimension',
                            'imageFields', 'created_at', 'updated_at',
                        }

                        missing_fields = validation_fields - data.keys()

                        if missing_fields:
                            assert not missing_fields, f'Missing fields {missing_fields} in {catalog.name} category_id: {category.id} part_id: {part_id}'
                        else:
                            image_fields = data.get('imageFields')

                            if image_fields:
                                validation_image_fields = {'name', 's3'}
                                image_missing_fields = validation_image_fields - image_fields.keys()

                                assert not image_missing_fields, f'Missing fields  {image_missing_fields} in imageFields => in {catalog.name} category_id: {category.id} part_id: {part_id}'
                            else:
                                assert image_fields, f'Not Image_fields in {catalog.name} category_id: {category.id} part_id: {part_id}'
                    else:
                        assert data, f'Note data_field in {catalog.name} category_id: {category.id} Part_id: {part_id})'

                    if part_category:
                        validation_fields = {'id'}
                        missing_fields = validation_fields - part_category.keys()

                        assert not missing_fields, f'Missing fields {missing_fields} in {catalog.name} category_id: {category.id} part_id: {part_id}'
                    else:
                        assert part_category, f'Note category_field in {catalog.name} category_id: {category.id} Part_id: {part_id})'

                else:
                    assert response.status_code == 200, f'Bad request {catalog.name} category_id: {category.id} part_id: {part_id}'







