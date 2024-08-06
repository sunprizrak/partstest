import time
from abc import ABC, abstractmethod
from progress.bar import IncrementalBar


class BaseTestCatalog(ABC):
    def _get_categories(self, catalog):
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

    @abstractmethod
    def test_tree(self, catalog):
        pass

    @abstractmethod
    def test_parts(self, catalog):
        pass


class TestLemkenCatalog(BaseTestCatalog):

    def test_tree(self, catalog):
        self._get_categories(catalog=catalog)

        if catalog.categories:
            subcategories = dict()
            parts_list = dict()

            bar = IncrementalBar(f'receive categories data from {catalog.name} ',
                                 max=len(list(catalog.categories)), suffix='%(index)d/%(max)d ')
            for category_id in list(catalog.categories):
                bar.next()
                time.sleep(0.1)
                response = catalog.get_category(category_id=category_id)

                if response.status_code != 200:
                    catalog.logger.warning(
                        f'Bad request catalog: {catalog.name} category_id: {category_id} {catalog.current_url}')
                    continue

                data = response.json().get('data')

                if not data:
                    catalog.logger.warning(f'Note data in catalog: {catalog.name} category_id: {category_id}')
                    continue

                for subcategory in data:
                    children = subcategory.get('children')

                    if not children:
                        catalog.logger.warning(
                            f'No children in data catalog: {catalog.name} category_id: {category_id}')
                        continue

                    for index, child in enumerate(children):
                        child_id = child.get('id')
                        subcategories[f"{index}_-_{category_id}"] = child_id
            bar.finish()

            bar = IncrementalBar(f'receive parts list', max=len(subcategories), suffix='%(index)d/%(max)d ')
            for category_data, subcategory_id in subcategories.items():
                category_id = category_data.split('_-_')[-1]
                bar.next()
                response = catalog.get_category(category_id=subcategory_id)

                if response.status_code != 200:
                    catalog.logger.warning(
                        f'Bad request catalog: {catalog.name} category_id: {category_id} subcategory_id: {subcategory_id} {catalog.current_url}')
                    continue

                data = response.json().get('data')

                if not data:
                    catalog.logger.warning(
                        f'No data in catalog: {catalog.name} category_id: {category_id} subcategory_id: {subcategory_id}')
                    continue

                for el in data:
                    children = el.get('children')

                    if not children:
                        catalog.logger.warning(
                            f'No children in data catalog: {catalog.name} category_id: {category_id} subcategory_id: {subcategory_id}')
                        continue

                    for index, child in enumerate(children):
                        child_id = child.get('id')
                        parts_list[f"{index}_-_{subcategory_id}_-_{category_id}"] = child_id
            bar.finish()

            bar = IncrementalBar(f'receive parts from parts list', max=len(parts_list), suffix='%(index)d/%(max)d ')
            for category_data, part_list_id in parts_list.items():
                _, subcategory_id, category_id = category_data.split('_-_')
                bar.next()
                response = catalog.get_parts(child_id=part_list_id)

                if response.status_code != 200:
                    catalog.logger.warning(
                        f'Bad request catalog: {catalog.name} category_id: {category_id} subcategory_id: {subcategory_id} part_list_id: {part_list_id} {catalog.current_url}')
                    continue

                data = response.json().get('data')

                if not data:
                    catalog.logger.warning(
                        f'No Parts in {catalog.name} category_id: {category_id} subcategory_id: {subcategory_id} part_list_id: {part_list_id}')
                    continue

                for part in data:
                    part_id = part.get('id')
                    category = catalog.categories[int(category_id)]
                    category.add_part(part_id=part_id)
            bar.finish()
        else:
            catalog.logger.warning(f'No Categories in {catalog.name}')

    def test_parts(self, catalog):
        parts = []

        for el in catalog.categories.values():
            parts.extend(el.parts)

        if parts:
            bar = IncrementalBar(f'check fields in detail', max=len(parts), suffix='%(index)d/%(max)d ')
            for part in parts:
                bar.next()
                response = catalog.get_part(part_id=part.id)

                if response.status_code != 200:
                    catalog.logger.warning(
                        f'Bad request catalog: {catalog.name} part_id: {part.id} {catalog.current_url}')
                    continue

                data = response.json().get('data')

                if not data:
                    catalog.logger.warning(f'No data in {catalog.name} Part_id: {part.id})')
                    continue

                part.validate(data=data)
            bar.finish()
        else:
            catalog.logger.warning(f'No parts in catalog: {catalog.name}')


class TestGrimmeCatalog(BaseTestCatalog):

    def test_tree(self, catalog):
        self._get_categories(catalog=catalog)

    def test_parts(self, catalog):
        pass


class TestKubotaCatalog(BaseTestCatalog):

    def test_tree(self, catalog):
        self._get_categories(catalog=catalog)

        if catalog.categories:
            subcategories = dict()
            two_subcategories = dict()
            parts_list = dict()

            bar = IncrementalBar(f'receive categories data from {catalog.name} ', max=len(list(catalog.categories)), suffix='%(index)d/%(max)d ')
            for category_id in list(catalog.categories):
                bar.next()
                time.sleep(0.1)
                response = catalog.get_category(category_id=category_id)

                if response.status_code != 200:
                    catalog.logger.warning(
                        f'Bad request catalog: {catalog.name} category_id: {category_id} {catalog.current_url}')
                    continue

                data = response.json().get('data')

                if not data:
                    catalog.logger.warning(f'Note data in catalog: {catalog.name} category_id: {category_id}')
                    continue

                for subcategory in data:
                    children = subcategory.get('children')

                    if not children:
                        catalog.logger.warning(
                            f'No children in data catalog: {catalog.name} category_id: {category_id}')
                        continue

                    for index, child in enumerate(children):
                        child_id = child.get('id')
                        subcategories[f"{index}_-_{category_id}"] = child_id
            bar.finish()

            bar = IncrementalBar(f'receive subcategories', max=len(subcategories), suffix='%(index)d/%(max)d ')
            for category_data, subcategory_id in subcategories.items():
                category_id = category_data.split('_-_')[-1]
                bar.next()
                response = catalog.get_category(category_id=subcategory_id)

                if response.status_code != 200:
                    catalog.logger.warning(
                        f'Bad request catalog: {catalog.name} category_id: {category_id} subcategory_id: {subcategory_id} {catalog.current_url}')
                    continue

                data = response.json().get('data')

                if not data:
                    catalog.logger.warning(
                        f'No data in catalog: {catalog.name} category_id: {category_id} subcategory_id: {subcategory_id}')
                    continue

                for el in data:
                    children = el.get('children')

                    if not children:
                        catalog.logger.warning(
                            f'No children in data catalog: {catalog.name} category_id: {category_id} subcategory_id: {subcategory_id}')
                        continue

                    for index, child in enumerate(children):
                        child_id = child.get('id')
                        two_subcategories[f"{index}_-_{subcategory_id}_-_{category_id}"] = child_id
            bar.finish()

            bar = IncrementalBar(f'receive parts list', max=len(two_subcategories), suffix='%(index)d/%(max)d ')
            for category_data, two_subcategory_id in two_subcategories.items():
                _, subcategory_id, category_id = category_data.split('_-_')
                bar.next()
                response = catalog.get_category(category_id=two_subcategory_id)

                if response.status_code != 200:
                    catalog.logger.warning(
                        f'Bad request catalog: {catalog.name} category_id: {category_id} subcategory_id: {subcategory_id} two_subcategory_id: {two_subcategory_id}  {catalog.current_url}')
                    continue

                data = response.json().get('data')

                if not data:
                    catalog.logger.warning(
                        f'No data in catalog: {catalog.name} category_id: {category_id} subcategory_id: {subcategory_id} two_subcategory_id: {two_subcategory_id}')
                    continue

                for index, part_list in enumerate(data):
                    part_list_id = part_list.get('id')
                    parts_list[f"{index}_-_{subcategory_id}_-_{two_subcategory_id}_-_{category_id}"] = part_list_id
            bar.finish()

            bar = IncrementalBar(f'receive parts from parts list', max=len(parts_list), suffix='%(index)d/%(max)d ')
            for category_data, part_list_id in parts_list.items():
                _, subcategory_id, two_subcategory_id, category_id = category_data.split('_-_')
                bar.next()
                response = catalog.get_parts(child_id=part_list_id)

                if response.status_code != 200:
                    catalog.logger.warning(
                        f'Bad request catalog: {catalog.name} category_id: {category_id} subcategory_id: {subcategory_id} two_subcategory_id: {two_subcategory_id} part_list_id: {part_list_id} {catalog.current_url}')
                    continue

                data = response.json().get('data')

                if not data:
                    catalog.logger.warning(
                        f'No Parts in {catalog.name} category_id: {category_id} subcategory_id: {subcategory_id} two_subcategory_id: {two_subcategory_id} part_list_id: {part_list_id}')
                    continue

                for part in data:
                    part_id = part.get('id')
                    category = catalog.categories[int(category_id)]
                    category.add_part(part_id=part_id)
            bar.finish()
        else:
            catalog.logger.warning(f'No Categories in {catalog.name}')

    def test_parts(self, catalog):
        parts = []

        for el in catalog.categories.values():
            parts.extend(el.parts)

        if parts:
            bar = IncrementalBar(f'check fields in detail', max=len(parts), suffix='%(index)d/%(max)d ')
            for part in parts:
                bar.next()
                response = catalog.get_part(part_id=part.id)

                if response.status_code != 200:
                    catalog.logger.warning(
                        f'Bad request catalog: {catalog.name} part_id: {part.id} {catalog.current_url}')
                    continue

                data = response.json().get('data')

                if not data:
                    catalog.logger.warning(f'No data in {catalog.name} Part_id: {part.id})')
                    continue

                part.validate(data=data)
            bar.finish()
        else:
            catalog.logger.warning(f'No parts in catalog: {catalog.name}')


class TestClaasCatalog(BaseTestCatalog):
    def test_tree(self, catalog):
        self._get_categories(catalog=catalog)

        if catalog.categories:
            subcategories = dict()
            two_subcategories = dict()
            parts_list = dict()

            bar = IncrementalBar(f'receive categories data from {catalog.name} ', max=len(list(catalog.categories)),
                                 suffix='%(index)d/%(max)d ')
            for category_id in list(catalog.categories):
                bar.next()
                time.sleep(0.1)
                response = catalog.get_category(category_id=category_id)

                if response.status_code != 200:
                    catalog.logger.warning(
                        f'Bad request catalog: {catalog.name} category_id: {category_id} {catalog.current_url}')
                    continue

                data = response.json().get('data')

                if not data:
                    catalog.logger.warning(f'Note data in catalog: {catalog.name} category_id: {category_id}')
                    continue

                for subcategory in data:
                    children = subcategory.get('children')

                    if not children:
                        catalog.logger.warning(
                            f'No children in data catalog: {catalog.name} category_id: {category_id}')
                        continue

                    for index, child in enumerate(children):
                        child_id = child.get('id')
                        subcategories[f"{index}_-_{category_id}"] = child_id
            bar.finish()

            bar = IncrementalBar(f'receive subcategories', max=len(subcategories), suffix='%(index)d/%(max)d ')
            for category_data, subcategory_id in subcategories.items():
                category_id = category_data.split('_-_')[-1]
                bar.next()
                response = catalog.get_category(category_id=subcategory_id)

                if response.status_code != 200:
                    catalog.logger.warning(
                        f'Bad request catalog: {catalog.name} category_id: {category_id} subcategory_id: {subcategory_id} {catalog.current_url}')
                    continue

                data = response.json().get('data')

                if not data:
                    catalog.logger.warning(
                        f'No data in catalog: {catalog.name} category_id: {category_id} subcategory_id: {subcategory_id}')
                    continue

                for el in data:
                    children = el.get('children')

                    if not children:
                        catalog.logger.warning(
                            f'No children in data catalog: {catalog.name} category_id: {category_id} subcategory_id: {subcategory_id}')
                        continue

                    for index, child in enumerate(children):
                        child_id = child.get('id')
                        two_subcategories[f"{index}_-_{subcategory_id}_-_{category_id}"] = child_id
            bar.finish()

            bar = IncrementalBar(f'receive parts list', max=len(two_subcategories), suffix='%(index)d/%(max)d ')
            for category_data, two_subcategory_id in two_subcategories.items():
                _, subcategory_id, category_id = category_data.split('_-_')
                bar.next()
                response = catalog.get_category(category_id=two_subcategory_id)

                if response.status_code != 200:
                    catalog.logger.warning(
                        f'Bad request catalog: {catalog.name} category_id: {category_id} subcategory_id: {subcategory_id} two_subcategory_id: {two_subcategory_id}  {catalog.current_url}')
                    continue

                data = response.json().get('data')

                if not data:
                    catalog.logger.warning(
                        f'No data in catalog: {catalog.name} category_id: {category_id} subcategory_id: {subcategory_id} two_subcategory_id: {two_subcategory_id}')
                    continue

                for index, part_list in enumerate(data):
                    part_list_id = part_list.get('id')
                    parts_list[f"{index}_-_{subcategory_id}_-_{two_subcategory_id}_-_{category_id}"] = part_list_id
            bar.finish()

            bar = IncrementalBar(f'receive parts from parts list', max=len(parts_list), suffix='%(index)d/%(max)d ')
            for category_data, part_list_id in parts_list.items():
                _, subcategory_id, two_subcategory_id, category_id = category_data.split('_-_')
                bar.next()
                response = catalog.get_parts(child_id=part_list_id)

                if response.status_code != 200:
                    catalog.logger.warning(
                        f'Bad request catalog: {catalog.name} category_id: {category_id} subcategory_id: {subcategory_id} two_subcategory_id: {two_subcategory_id} part_list_id: {part_list_id} {catalog.current_url}')
                    continue

                data = response.json().get('data')

                if not data:
                    catalog.logger.warning(
                        f'No Parts in {catalog.name} category_id: {category_id} subcategory_id: {subcategory_id} two_subcategory_id: {two_subcategory_id} part_list_id: {part_list_id}')
                    continue

                for part in data:
                    part_id = part.get('id')
                    category = catalog.categories[int(category_id)]
                    category.add_part(part_id=part_id)
            bar.finish()
        else:
            catalog.logger.warning(f'No Categories in {catalog.name}')

    def test_parts(self, catalog):
        parts = []

        for el in catalog.categories.values():
            parts.extend(el.parts)

        if parts:
            bar = IncrementalBar(f'check fields in detail', max=len(parts), suffix='%(index)d/%(max)d ')
            for part in parts:
                bar.next()
                response = catalog.get_part(part_id=part.id)

                if response.status_code != 200:
                    catalog.logger.warning(f'Bad request catalog: {catalog.name} part_id: {part.id} {catalog.current_url}')
                    continue

                data = response.json().get('data')

                if not data:
                    catalog.logger.warning(f'No data in {catalog.name} Part_id: {part.id})')
                    continue

                part.validate(data=data)
            bar.finish()
        else:
            catalog.logger.warning(f'No parts in catalog: {catalog.name}')


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




