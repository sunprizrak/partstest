import time
from abc import ABC, abstractmethod
from progress.bar import IncrementalBar


class NoDataException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class CatalogTestUtility:

    @staticmethod
    def get_children(categories: list, test_api, part_list=None):
        children = []
        bar_message = "receive children"
        bar = IncrementalBar(
            message=bar_message,
            max=len(categories),
            suffix='%(index)d/%(max)d ',
        )
        for category in categories:
            bar.message = f"{bar_message} from {category}"
            bar.next()
            resp = category.get_children(test_api, part_list)

            if resp:
                if test_api:
                    resp = resp[:1]

                children.extend(resp)

        bar.finish()
        return children


class TestCatalogBase(ABC, CatalogTestUtility):

    def test_root_categories(self, catalog, test_api):
        data = catalog.get_data_root_categories()
        if data:
            bar = IncrementalBar(f'receive categories from {catalog.name} ', max=len(data), suffix='%(index)d/%(max)d ')
            for category_data in data:
                bar.next()

                if test_api:
                    time.sleep(0.2)
                else:
                    time.sleep(0.1)

                category = catalog.add_category(data=category_data)
                category.validate(data=category_data)
            bar.finish()
        else:
            catalog.logger.warning(f'No data in {catalog.current_url} catalog: {catalog.name}')

    @abstractmethod
    def test_tree(self, catalog, test_api):
        pass

    def test_parts(self, catalog, test_api):

        for category in catalog.categories.values():
            if category.part_lists:
                category.get_parts(test_api)
            else:
                catalog.logger.warning(f'No PARTLISTS in {catalog.name} category_name: {category.name} category_id: {category.id})')

        parts = []

        for category in catalog.categories.values():
            if category.parts:
                parts.extend(category.parts)
            else:
                catalog.logger.warning(f'No PARTS in {catalog.name} category_name: {category.name} category_id: {category.id})')

        if parts:
            bar = IncrementalBar(f'validate details in {catalog.name}', max=len(parts), suffix='%(index)d/%(max)d ')
            for part in parts:
                bar.next()

                if test_api:
                    time.sleep(0.2)

                response = catalog.get_part(part_id=part.id)

                if response.status_code != 200:
                    catalog.logger.warning(
                        f'Bad request catalog: {catalog.name} part_id: {part.id} {catalog.current_url}')
                    continue

                data = response.json().get('data')
                # for test
                print('\n')
                for key, val in data.items():
                    print(f"{key}: {val}")
                # end test
                if not data:
                    catalog.logger.warning(f'No data in {catalog.name} Part_id: {part.id})')
                    continue

                part.validate(data=data)
            bar.finish()
        else:
            catalog.logger.warning(f'No parts in catalog: {catalog.name}')


class TestLemkenCatalog(TestCatalogBase):

    def test_tree(self, catalog, test_api):
        if catalog.categories:
            state_while = True
            index = 0

            while state_while:
                categories = list(catalog.categories.values())

                if test_api:
                    categories = [list(catalog.categories.values())[index]]

                level_1 = self.get_children(categories=categories, test_api=test_api)

                if level_1:
                    level_2 = self.get_children(categories=level_1, test_api=test_api)

                    if level_2:
                        if test_api:
                            category = categories[0]
                            category.add_part_lists(level_2)
                            state_while = False
                        else:
                            for part_list in level_2:
                                category = catalog.categories[part_list.root_id]
                                category.add_part_lists(part_list)
                            index += 1
                    else:
                        index += 1
                else:
                    index += 1

                if index >= len(catalog.categories):
                    state_while = False
        else:
            catalog.logger.warning(f'No Categories in {catalog.name}')


class TestGrimmeCatalog(TestCatalogBase):

    def test_tree(self, catalog, test_api):
        if catalog.categories:
            state_while = True
            index = 0

            while state_while:
                categories = list(catalog.categories.values())

                if test_api:
                    categories = [list(catalog.categories.values())[index]]

                level_1 = self.get_children(categories=categories, test_api=test_api)

                if level_1:
                    level_2 = self.get_children(categories=level_1, test_api=test_api)

                    if level_2:
                        level_3 = self.get_children(categories=level_2, test_api=test_api)

                        if level_3:
                            level_4 = self.get_children(categories=level_3, test_api=test_api)

                            if level_4:
                                if test_api:
                                    category = categories[0]
                                    category.add_part_lists(level_4)
                                    state_while = False
                                else:
                                    for part_list in level_3:
                                        category = catalog.categories[part_list.root_id]
                                        category.add_part_lists(part_list)
                                    index += 1
                            else:
                                index += 1
                        else:
                            index += 1
                    else:
                        index += 1
                else:
                    index += 1

                if index >= len(catalog.categories):
                    state_while = False
        else:
            catalog.logger.warning(f'No Categories in {catalog.name}')


class TestKubotaCatalog(TestCatalogBase):

    def test_tree(self, catalog, test_api):
        if catalog.categories:
            state_while = True
            index = 0

            while state_while:
                categories = list(catalog.categories.values())

                if test_api:
                    categories = [list(catalog.categories.values())[index]]

                level_1 = self.get_children(categories=categories, test_api=test_api)

                if level_1:
                    level_2 = self.get_children(categories=level_1, test_api=test_api)

                    if level_2:
                        if test_api:
                            category = categories[0]
                            category.add_part_lists(level_2)
                            state_while = False
                        else:
                            for part_list in level_2:
                                category = catalog.categories[part_list.root_id]
                                category.add_part_lists(part_list)
                            index += 1
                    else:
                        index += 1
                else:
                    index += 1

                if index >= len(catalog.categories):
                    state_while = False
        else:
            catalog.logger.warning(f'No Categories in {catalog.name}')


class TestClaasCatalog(TestCatalogBase):

    def test_tree(self, catalog, test_api):
        if catalog.categories:
            state_while = True
            index = 0

            while state_while:
                categories = list(catalog.categories.values())

                if test_api:
                    categories = [list(catalog.categories.values())[index]]

                level_1 = self.get_children(categories=categories, test_api=test_api)

                if level_1:
                    level_2 = self.get_children(categories=level_1, test_api=test_api)

                    if level_2:
                        level_3 = self.get_children(categories=level_2, test_api=test_api)

                        if level_3:
                            if test_api:
                                category = categories[0]
                                category.add_part_lists(level_3)
                                state_while = False
                            else:
                                for part_list in level_3:
                                    category = catalog.categories[part_list.root_id]
                                    category.add_part_lists(part_list)
                                index += 1
                        else:
                            index += 1
                    else:
                        index += 1
                else:
                    index += 1

                if index >= len(catalog.categories):
                    state_while = False
        else:
            catalog.logger.warning(f'No Categories in {catalog.name}')


class TestKroneCatalog(TestCatalogBase):

    def test_tree(self, catalog, test_api):
        if catalog.categories:
            state_while = True
            index = 0

            while state_while:
                categories = list(catalog.categories.values())

                if test_api:
                    categories = [list(catalog.categories.values())[index]]

                level_1 = self.get_children(categories=categories, test_api=test_api)

                if level_1:
                    level_2 = self.get_children(categories=level_1, test_api=test_api)

                    if level_2:
                        level_3 = self.get_children(categories=level_2, test_api=test_api, part_list=True)

                        if level_3:
                            if test_api:
                                category = categories[0]
                                category.add_part_lists(level_3)
                                state_while = False
                            else:
                                for part_list in level_3:
                                    category = catalog.categories[part_list.root_id]
                                    category.add_part_lists(part_list)
                                index += 1
                        else:
                            index += 1
                    else:
                        index += 1
                else:
                    index += 1

                if index >= len(catalog.categories):
                    state_while = False
        else:
            catalog.logger.warning(f'No Categories in {catalog.name}')


class TestKvernelandCatalog(TestCatalogBase):

    def test_tree(self, catalog, test_api):
        if catalog.categories:
            state_while = True
            index = 0

            while state_while:
                categories = list(catalog.categories.values())

                if test_api:
                    categories = [list(catalog.categories.values())[index]]

                level_1 = self.get_children(categories=categories, test_api=test_api)

                if level_1:
                    level_2 = self.get_children(categories=level_1, test_api=test_api)

                    if level_2:
                        if test_api:
                            category = categories[0]
                            category.add_part_lists(level_2)
                            state_while = False
                        else:
                            for part_list in level_2:
                                category = catalog.categories[part_list.root_id]
                                category.add_part_lists(part_list)
                            index += 1
                    else:
                        index += 1
                else:
                    index += 1

                if index >= len(catalog.categories):
                    state_while = False
        else:
            catalog.logger.warning(f'No Categories in {catalog.name}')


class TestRopaCatalog(TestCatalogBase):

    def test_tree(self, catalog, test_api):
        if catalog.categories:
            state_while = True
            index = 0

            while state_while:
                categories = list(catalog.categories.values())

                if test_api:
                    categories = [list(catalog.categories.values())[index]]

                level_1 = self.get_children(categories=categories, test_api=test_api)

                if level_1:
                    level_2 = self.get_children(categories=level_1, test_api=test_api)

                    if level_2:
                        if test_api:
                            category = categories[0]
                            category.add_part_lists(level_2)
                            state_while = False
                        else:
                            for part_list in level_2:
                                category = catalog.categories[part_list.root_id]
                                category.add_part_lists(part_list)
                            index += 1
                    else:
                        index += 1
                else:
                    index += 1

                if index >= len(catalog.categories):
                    state_while = False
        else:
            catalog.logger.warning(f'No Categories in {catalog.name}')


class TestJdeereCatalog(TestCatalogBase):

    def test_tree(self, catalog, test_api):
        if catalog.categories:
            state_while = True
            index = 0

            while state_while:
                categories = list(catalog.categories.values())

                if test_api:
                    categories = [list(catalog.categories.values())[index]]

                level_1 = self.get_children(categories=categories, test_api=test_api)

                if level_1:
                    level_2 = self.get_children(categories=level_1, test_api=test_api)

                    if level_2:
                        level_3 = self.get_children(categories=level_2, test_api=test_api, part_list=True)

                        if level_3:
                            if test_api:
                                category = categories[0]
                                category.add_part_lists(level_3)
                                state_while = False
                            else:
                                for part_list in level_3:
                                    category = catalog.categories[part_list.root_id]
                                    category.add_part_lists(part_list)
                                index += 1
                        else:
                            index += 1
                    else:
                        index += 1
                else:
                    index += 1

                if index >= len(catalog.categories):
                    state_while = False
        else:
            catalog.logger.warning(f'No Categories in {catalog.name}')


class TestCatalog:
    """class wrap for start test"""

    @staticmethod
    def _get_test_instance(catalog):
        catalog_name = catalog.name.capitalize()
        test_class_name = f"Test{catalog_name}Catalog"
        test_class = globals().get(test_class_name)

        if test_class is None:
            raise ValueError(f"Test class {test_class_name} is not defined.")

        return test_class()

    def test_root_categories(self, catalog, test_api):
        instance = self._get_test_instance(catalog)
        instance.test_root_categories(catalog, test_api)

    def test_tree(self, catalog, test_api):
        instance = self._get_test_instance(catalog)
        instance.test_tree(catalog, test_api)

    def test_parts(self, catalog, test_api):
        instance = self._get_test_instance(catalog)
        instance.test_parts(catalog, test_api)




