import time
from abc import ABC, abstractmethod

from progress.bar import IncrementalBar


class BaseTestCatalog(ABC):

    @abstractmethod
    def test_tree(self, catalog):
        pass

    @abstractmethod
    def test_parts(self, catalog):
        pass


class TestLemkenCatalog(BaseTestCatalog):

    def test_tree(self, catalog):
        print(catalog.name)
        print(self.__class__.__name__)
        response = catalog.get_tree()

        if response.status_code == 200:
            data = response.json().get('data')
            if data:
                bar = IncrementalBar(f'{catalog.name} categories', max=len(data), suffix='%(index)d/%(max)d ')
                for category_data in data:
                    bar.next()
                    time.sleep(0.2)
                    category_id = category_data.get('id')

                    catalog.add_category(category_id=category_id)
                    catalog.categories[category_id].validate(data=category_data)

                bar.finish()
            else:
                catalog.logger.warning(f'No data in {catalog.name} {catalog.current_url}')
        else:
            catalog.logger.warning(f'Bad request {catalog.name} {catalog.current_url}')

        if catalog.categories:
            main_parts_list_ids = []

            bar = IncrementalBar(f'receive categories data from {catalog.name} ', max=len(list(catalog.categories)[-2:]),
                                 suffix='%(index)d/%(max)d ')
            for category_id in list(catalog.categories)[-2:]:
                bar.next()
                time.sleep(0.1)
                response = catalog.get_category(category_or_children_id=category_id)

                if response.status_code != 200:
                    catalog.logger.warning(
                        f'Bad request catalog: {catalog.name} category_id: {category_id} {catalog.current_url}')
                    continue

                data = response.json().get('data')

                if not data:
                    catalog.logger.warning(f'Note data in catalog: {catalog.name} category_id: {category_id}')
                    continue

                for el in data:
                    children = el.get('children')

                    if not children:
                        catalog.logger.warning(
                            f'No children in data catalog: {catalog.name} category_id: {category_id}')
                        continue

                    for child in children:
                        child_id = child.get('id')
                        main_parts_list_ids.append(child_id)
            bar.finish()

            children_parts_list_ids = []

            bar = IncrementalBar(f'receive parts list', max=len(main_parts_list_ids), suffix='%(index)d/%(max)d ')
            for part_list_id in main_parts_list_ids:
                bar.next()
                response = catalog.get_category(category_or_children_id=part_list_id)

                if response.status_code != 200:
                    catalog.logger.warning(
                        f'Bad request catalog: {catalog.name} part_list_id: {part_list_id} {catalog.current_url}')
                    continue

                data = response.json().get('data')

                if not data:
                    catalog.logger.warning(f'No data in catalog: {catalog.name} main_part_list_id: {part_list_id}')
                    continue

                for el in data:
                    children = el.get('children')

                    if not children:
                        catalog.logger.warning(
                            f'No children in data catalog: {catalog.name} main_part_list_id: {part_list_id}')
                        continue

                    for child in children:
                        child_id = child.get('id')
                        children_parts_list_ids.append(child_id)
            bar.finish()

            bar = IncrementalBar(f'receive parts from parts list', max=len(children_parts_list_ids), suffix='%(index)d/%(max)d ')
            for part_list_id in children_parts_list_ids:
                bar.next()
                response = catalog.get_parts(child_id=part_list_id)

                if response.status_code != 200:
                    catalog.logger.warning(
                        f'Bad request catalog: {catalog.name} part_list_id: {part_list_id} {catalog.current_url}')
                    continue

                data = response.json().get('data')

                if not data:
                    catalog.logger.warning(f'No Parts in {catalog.name} part_list_id: {part_list_id}')
                    continue

                for part in data:
                    part_id = part.get('id')
                    catalog.parts.append(part_id)

            bar.finish()
        else:
            catalog.logger.warning(f'No Categories in {catalog.name}')

    def test_parts(self, catalog):
        pass


class TestCatalog:
    """class wrap for start test"""
    def _get_test_instance(self, catalog):
        catalog_name = catalog.name.capitalize()
        test_class_name = f"Test{catalog_name}Catalog"
        test_class = globals().get(test_class_name)

        if test_class is None:
            raise ValueError(f"Test class {test_class_name} is not defined.")

        return test_class()

    def test_tree(self, catalog):
        instance = self._get_test_instance(catalog)
        instance.test_tree(catalog)

    def test_parts(self, catalog):
        instance = self._get_test_instance(catalog)
        instance.test_parts(catalog)


    # def test_tree(self, catalog):
    #     response = catalog.get_tree()
    #
    #     if response.status_code == 200:
    #         data = response.json().get('data')
    #         if data:
    #             bar = IncrementalBar(f'{catalog.name} categories', max=len(data), suffix='%(index)d/%(max)d ')
    #             for category_data in data:
    #                 bar.next()
    #                 time.sleep(0.2)
    #                 category_id = category_data.get('id')
    #
    #                 catalog.add_category(category_id=category_id)
    #                 catalog.categories[category_id].validate(data=category_data)
    #
    #             bar.finish()
    #         else:
    #             catalog.logger.warning(f'No data in {catalog.name} {catalog.current_url}')
    #     else:
    #         catalog.logger.warning(f'Bad request {catalog.name} {catalog.current_url}')
    #
    #     if catalog.categories:
    #         bar = IncrementalBar(f'receive categories data from {catalog.name} ', max=len(list(catalog.categories)[-2:]), suffix='%(index)d/%(max)d ')
    #         for category_id in list(catalog.categories)[-2:]:
    #             bar.next()
    #             time.sleep(0.1)
    #             response = catalog.get_category(category_or_children_id=category_id)
    #
    #             if response.status_code != 200:
    #                 catalog.logger.warning(f'Bad request catalog: {catalog.name} category_id: {category_id} {catalog.current_url}')
    #                 continue
    #
    #             data = response.json().get('data')
    #
    #             if not data:
    #                 catalog.logger.warning(f'Note data in catalog: {catalog.name} category_id: {category_id}')
    #                 continue
    #
    #             for subcategory in data:
    #                 children = subcategory.get('children')
    #
    #                 if not children:
    #                     catalog.logger.warning(f'No children in data catalog: {catalog.name} category_id: {category_id}')
    #                     continue
    #
    #                 for child in children:
    #                     child_id = child.get('id')
    #                     catalog.categories[category_id].subcategories.append(child_id)
    #         bar.finish()
    #
    #         for category_id in list(catalog.categories)[-2:]:
    #             catalog.categories[category_id].get_parts()
    #
    #     else:
    #         catalog.logger.warning(f'No Categories in {catalog.name}')
    #
    # def test_parts(self, catalog):
    #     if catalog.parts:
    #         bar = IncrementalBar(f'check fields in detail', max=len(catalog.parts), suffix='%(index)d/%(max)d ')
    #         for part_id in catalog.parts:
    #             bar.next()
    #             response = catalog.get_part(part_id=part_id)
    #
    #             if response.status_code != 200:
    #                 catalog.logger.warning(f'Bad request catalog: {catalog.name} part_id: {part_id} {catalog.current_url}')
    #                 continue
    #
    #             data = response.json().get('data')
    #
    #             if not data:
    #                 catalog.logger.warning(f'No data in {catalog.name} Part_id: {part_id})')
    #                 continue
    #
    #             validation_fields = {
    #                 'id', 'name', 'link_type', 'quantity',
    #                 'part_number', 'position', 'dimension',
    #                 'imageFields', 'created_at', 'updated_at',
    #             }
    #
    #             missing_fields = validation_fields - data.keys()
    #
    #             if len(missing_fields) > 0:
    #                 catalog.logger.warning(f'Missing fields {missing_fields} in {catalog.name} part_id: {part_id}')
    #
    #             image_fields = data.get('imageFields')
    #
    #             if image_fields:
    #                 validation_image_fields = {'name', 's3'}
    #
    #                 image_missing_fields = validation_image_fields - image_fields.keys()
    #
    #                 if len(image_missing_fields) > 0:
    #                     catalog.logger.warning(f'Missing fields  {image_missing_fields} in imageFields => in {catalog.name} part_id: {part_id}')
    #             else:
    #                 catalog.logger.warning(f'Not Image_fields in {catalog.name} part_id: {part_id}')
    #
    #             part_category = response.json().get('category')
    #
    #             if part_category:
    #                 validation_fields = {'id'}
    #                 missing_fields = validation_fields - part_category.keys()
    #
    #                 if len(missing_fields) > 0:
    #                     catalog.logger.warning(f'Missing fields {missing_fields} in {catalog.name} part_id: {part_id}')
    #             else:
    #                 catalog.logger.warning(f'No part_category in {catalog.name} part_id: {part_id}')
    #         bar.finish()
    #     else:
    #         catalog.logger.warning(f'No parts in catalog: {catalog.name}')






