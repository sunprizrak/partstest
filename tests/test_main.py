import time

import pytest
from src.main import Catalog, Category
from progress.bar import IncrementalBar


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
                bar = IncrementalBar(f'{catalog.name} categories', max=len(data))

                for category in data:
                    bar.next()
                    time.sleep(0.2)
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
                bar.finish()
            else:
                assert data, f'Note Categories in {catalog.name}'
        else:
            assert response.status_code == 200, f'Bad request {catalog.current_url}'

    @pytest.mark.dependency(name='test_category', depends=["test_tree"])
    def test_category(self, catalog):
        main_parts_list_ids = []

        bar = IncrementalBar(f'receive categories data from {catalog.name} ', max=len(catalog.categories[-1:]))
        for category in catalog.categories[-1:]:
            bar.next()
            time.sleep(0.1)
            response = catalog.get_category(category_or_children_id=category.id)
            assert response.status_code == 200, f'Bad request catalog: {catalog.current_url}'

            data = response.json().get('data')
            assert data, f'Note data in catalog: {catalog.name} category_id: {category.id}'

            for el in data:
                children = el.get('children')
                assert children, f'No children in data catalog: {catalog.name} category_id: {category.id}'

                for child in children:
                    child_id = child.get('id')
                    main_parts_list_ids.append(child_id)
        bar.finish()

        children_parts_list_ids = []

        bar = IncrementalBar(f'receive parts list', max=len(main_parts_list_ids))
        for part_list_id in main_parts_list_ids:
            bar.next()
            response = catalog.get_category(category_or_children_id=part_list_id)
            assert response.status_code == 200, f'Bad request {catalog.current_url}'

            data = response.json().get('data')
            assert data, f'Note data in catalog: {catalog.name} main_part_list_id: {part_list_id}'

            for el in data:
                children = el.get('children')
                assert children, f'No children in data catalog: {catalog.name} main_part_list_id: {part_list_id}'

                for child in children:
                    child_id = child.get('id')
                    children_parts_list_ids.append(child_id)
        bar.finish()

        bar = IncrementalBar(f'receive parts from parts list', max=len(children_parts_list_ids))
        for part_list_id in children_parts_list_ids:
            bar.next()
            response = catalog.get_parts(child_id=part_list_id)
            assert response.status_code == 200, f'Bad request {catalog.current_url}'

            data = response.json().get('data')
            assert data, f'Note Parts in {catalog.name} part_list_id: {part_list_id}'

            for part in data:
                part_id = part.get('id')
                catalog.parts.append(part_id)

        bar.finish()

    @pytest.mark.dependency(depends=["test_category"])
    def test_part(self, catalog):
        bar = IncrementalBar(f'check fields in detail', max=len(catalog.parts))
        for part_id in catalog.parts:
            bar.next()
            response = catalog.get_part(part_id=part_id)
            assert response.status_code == 200, f'Bad request {catalog.current_url}'

            data = response.json().get('data')
            assert data, f'Note data_field in {catalog.name} Part_id: {part_id})'

            validation_fields = {
                'id', 'name', 'link_type', 'quantity',
                'part_number', 'position', 'dimension',
                'imageFields', 'created_at', 'updated_at',
            }

            missing_fields = validation_fields - data.keys()
            assert not missing_fields, f'Missing fields {missing_fields} in {catalog.name} part_id: {part_id}'

            image_fields = data.get('imageFields')
            assert image_fields, f'Not Image_fields in {catalog.name} art_id: {part_id}'

            validation_image_fields = {'name', 's3'}

            image_missing_fields = validation_image_fields - image_fields.keys()
            assert not image_missing_fields, f'Missing fields  {image_missing_fields} in imageFields => in {catalog.name} part_id: {part_id}'

            part_category = response.json().get('category')
            assert part_category, f'Note category_field in {catalog.name} Part_id: {part_id})'

            validation_fields = {'id'}
            missing_fields = validation_fields - part_category.keys()

            assert not missing_fields, f'Missing fields {missing_fields} in {catalog.name} part_id: {part_id}'
        bar.finish()







