import pytest
from src.main import Catalog, Category


@pytest.mark.parametrize('catalog', Catalog.objects)
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
                    elif catalog.name == 'claas':
                        validation_fields = {
                            'id', 'name', 'parent_id', 'link_type',
                            'depth', 'children', 'created_at', 'updated_at',
                        }

                    missing_fields = validation_fields - category.keys()

                    assert not missing_fields, f'Missing fields {missing_fields} in {catalog.name}'

                    category_id = category.get('id')
                    obj = Category(category_id=category_id)
                    catalog.categories.append(obj)
            else:
                assert data, f'Note Categories in {catalog.name}'
        else:
            error_message = response.json().get('message')
            assert response.status_code == 200, f'Bad request {catalog.name}: {error_message}'

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
                                    error_message = response.json().get('message')
                                    assert response.status_code == 200, f'Bad request in {catalog.name} category_id: {category.id} external_id(part list): {external_id} : {error_message}'
                        else:
                            assert children, f'No children(Parts list) in {catalog.name} category_id: {category.id} data'
                else:
                    assert data, f'Note Category Data in {catalog.name} category_id: {category.id}'
            else:
                error_message = response.json().get('message')
                assert response.status_code == 200, f'Bad request {catalog.name}: {error_message}'

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
                    error_message = response.json().get('message')
                    assert response.status_code == 200, f'Bad request {catalog.name} category_id: {category.id} part_id: {part_id}: {error_message}'







