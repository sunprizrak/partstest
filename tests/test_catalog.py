import time
from abc import ABC, abstractmethod
from progress.bar import IncrementalBar


class NoDataException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class BaseTestCatalog(ABC):

    def test_root_categories(self, catalog):
        response = catalog.get_tree()

        if response.status_code == 200:
            data = response.json().get('data')
            if data:
                bar = IncrementalBar(f'{catalog.name} categories', max=len(data), suffix='%(index)d/%(max)d ')
                for category_data in data:
                    bar.next()
                    time.sleep(0.1)
                    catalog.add_category(data=category_data)
                bar.finish()
            else:
                catalog.logger.warning(f'No data in {catalog.name} {catalog.current_url}')
        else:
            catalog.logger.warning(f'Bad request {catalog.name} {catalog.current_url}')

    @abstractmethod
    def test_tree(self, catalog):
        pass

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


class TestLemkenCatalog(BaseTestCatalog):

    def test_tree(self, catalog):
        self._get_root_categories(catalog=catalog)

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


class TestGrimmeCatalog(BaseTestCatalog):

    def test_tree(self, catalog):
        response = catalog.get_tree()

        if response.status_code == 200:
            data = response.json().get('data')

            if data:
                bar = IncrementalBar(f'{catalog.name} categories', max=len(data), suffix='%(index)d/%(max)d ')
                for category_data in data:
                    bar.next()
                    time.sleep(0.1)
                    category_id = category_data.get('id')
                    catalog.add_category(category_id=category_id)
                    catalog.categories[category_id].validate(data=category_data)

                    models = category_data.get('children')

                    if not models:
                        catalog.logger.warning(
                            f'No children(models) in data catalog: {catalog.name} category_id: {category_id}')
                        continue

                    for model in models:
                        model_id = model.get('id')

                        modifications = model.get('children')

                        if not modifications:
                            catalog.logger.warning(
                                f'No children in data catalog: {catalog.name} category_id: {category_id} model_id: {model_id}')
                            continue

                        for modification in modifications:
                            modification_id = modification.get('id')
                            catalog.categories[category_id].modifications.append(f"{category_id}_-_{modification_id}")
                bar.finish()

                modifications = []

                for el in catalog.categories.values():
                    modifications.extend(el.modifications)

                node_groups = []

                bar = IncrementalBar(f'receive node_groups from modifications', max=len(modifications), suffix='%(index)d/%(max)d ')
                for modification in modifications:
                    bar.next()
                    category_id, modification_id = modification.split('_-_')
                    response = catalog.get_category(category_id=int(modification_id))

                    if response.status_code != 200:
                        catalog.logger.warning(
                            f'Bad request catalog: {catalog.name} category_id: {modification_id} {catalog.current_url}')
                        continue

                    data = response.json().get('data')

                    if not data:
                        catalog.logger.warning(
                            f'No data in catalog: {catalog.name} category_id: {modification_id}')
                        continue

                    for node_group in data:
                        node_group_id = node_group.get('id')
                        node_groups.append(f"{category_id}_-_{node_group_id}")
                bar.finish()

                nodes = []

                bar = IncrementalBar(f'receive node from node_groups', max=len(node_groups), suffix='%(index)d/%(max)d ')
                for node_group in node_groups:
                    bar.next()
                    category_id, node_group_id = node_group.split('_-_')
                    response = catalog.get_category(category_id=int(node_group_id))

                    if response.status_code != 200:
                        catalog.logger.warning(
                            f'Bad request catalog: {catalog.name} category_id: {node_group_id} {catalog.current_url}')
                        continue

                    data = response.json().get('data')

                    if not data:
                        catalog.logger.warning(
                            f'No data in catalog: {catalog.name} category_id: {node_group_id}')
                        continue

                    for node in data:
                        node_id = node.get('id')
                        nodes.append(f"{category_id}_-_{node_id}")
                bar.finish()

                bar = IncrementalBar(f'receive parts from nodes', max=len(nodes), suffix='%(index)d/%(max)d ')
                for node in nodes:
                    bar.next()
                    category_id, node_id = node.split('_-_')
                    response = catalog.get_category(category_id=int(node_id))

                    if response.status_code != 200:
                        catalog.logger.warning(
                            f'Bad request catalog: {catalog.name} category_id: {node_id} {catalog.current_url}')
                        continue

                    data = response.json().get('data')

                    if not data:
                        catalog.logger.warning(
                            f'No data in catalog: {catalog.name} category_id: {node_id}')
                        continue

                    for part in data:
                        part_id = part.get('id')
                        category = catalog.categories[int(category_id)]
                        category.add_part(part_id=part_id)
                bar.finish()
            else:
                catalog.logger.warning(f'No data in {catalog.name} {catalog.current_url}')
        else:
            catalog.logger.warning(f'Bad request {catalog.name} {catalog.current_url}')


class TestKubotaCatalog(BaseTestCatalog):

    def test_tree(self, catalog):
        self._get_root_categories(catalog=catalog)

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
        self._get_root_categories(catalog=catalog)

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


class TestKroneCatalog(BaseTestCatalog):

    def test_tree(self, catalog):
        self._get_root_categories(catalog=catalog)

        if catalog.categories:
            part_groups = dict()
            part_lists = dict()

            bar = IncrementalBar(f'receive PART_GROUPS from {catalog.name} categories', max=len(list(catalog.categories)),
                                 suffix='%(index)d/%(max)d ')
            for category_id in list(catalog.categories):
                bar.next()
                response = catalog.get_category(category_id=category_id)

                if response.status_code != 200:
                    catalog.logger.warning(
                        f'Bad request catalog: {catalog.name} category_id: {category_id} {catalog.current_url}')
                    continue

                data = response.json().get('data')

                if not data:
                    catalog.logger.warning(f'Note data in catalog: {catalog.name} category_id: {category_id}')
                    continue

                children = data[0].get('children')

                if not children:
                    catalog.logger.warning(
                        f'No children in data catalog: {catalog.name} category_id: {category_id}')
                    continue

                for part_group in children:
                    part_group_id = part_group.get('id')
                    response2 = catalog.get_category(category_id=part_group_id)

                    if response.status_code != 200:
                        catalog.logger.warning(
                            f'Bad request {catalog.current_url}: {catalog.name} category_id: {category_id} part_group: {part_group_id}')
                        continue

                    data2 = response2.json().get('data')

                    if not data2:
                        catalog.logger.warning(f'Note data in catalog: {catalog.name} category_id: {category_id} part_group: {part_group_id}')
                        continue

                    children2 = data2[0].get('children')

                    if not children2:
                        catalog.logger.warning(
                            f'No children in data catalog: {catalog.name} category_id: {category_id} part_group_id: {part_group_id}')
                        continue

                    for index, part_group2 in enumerate(children2):
                        part_group2_id = part_group2.get('id')
                        part_groups[f"{index}_-_{category_id}"] = part_group2_id
            bar.finish()

            bar = IncrementalBar(f'receive PART_LISTS from PART_GROUPS', max=len(part_groups), suffix='%(index)d/%(max)d ')
            for category_data, part_group_id in part_groups.items():
                bar.next()
                category_id = category_data.split('_-_')[-1]
                response = catalog.get_category(category_id=part_group_id)

                if response.status_code != 200:
                    catalog.logger.warning(
                        f'Bad request {catalog.current_url}: {catalog.name} category_id: {category_id} part_group_id: {part_group_id}')
                    continue

                data = response.json().get('data')

                if not data:
                    catalog.logger.warning(
                        f'No data in catalog: {catalog.name} category_id: {category_id} part_group_id: {part_group_id}')
                    continue

                for index, part_list in enumerate(data):
                    part_list_id = part_list.get('id')
                    part_lists[f"{index}_-_{part_group_id}_-_{category_id}"] = part_list_id
            bar.finish()

            bar = IncrementalBar(f'receive parts from part_lists', max=len(part_lists), suffix='%(index)d/%(max)d ')
            for category_data, part_list_id in part_lists.items():
                bar.next()
                _, part_group_id, category_id = category_data.split('_-_')
                response = catalog.get_parts(child_id=part_list_id)

                if response.status_code != 200:
                    catalog.logger.warning(
                        f'Bad request {catalog.current_url}: {catalog.name} category_id: {category_id} part_group_id: {part_group_id} part_list_id: {part_list_id}')
                    continue

                data = response.json().get('data')

                if not data:
                    catalog.logger.warning(
                        f'No Parts in {catalog.name} category_id: {category_id} part_group_id: {part_group_id} part_list_id: {part_list_id}')
                    continue

                for part in data:
                    part_id = part.get('id')
                    category = catalog.categories[int(category_id)]
                    category.add_part(part_id=part_id)
            bar.finish()
        else:
            catalog.logger.warning(f'No Categories in {catalog.name}')


class TestKvernelandCatalog(BaseTestCatalog):

    def test_tree(self, catalog):
        self._get_root_categories(catalog=catalog)

        if catalog.categories:
            subcategories = dict()
            part_lists = dict()

            bar = IncrementalBar(f'receive subcategories from {catalog.name} categories',
                                 max=len(list(catalog.categories)[:1]),
                                 suffix='%(index)d/%(max)d ')
            for category_id in list(catalog.categories)[:1]:
                bar.next()
                response = catalog.get_category(category_id=category_id)

                if response.status_code != 200:
                    catalog.logger.warning(
                        f'Bad request catalog: {catalog.name} category_id: {category_id} {catalog.current_url}')
                    continue

                data = response.json().get('data')

                if not data:
                    catalog.logger.warning(f'Note data in catalog: {catalog.name} category_id: {category_id}')
                    continue

                children = data[0].get('children')

                if not children:
                    catalog.logger.warning(
                        f'No children in data catalog: {catalog.name} category_id: {category_id}')
                    continue

                for child in children:
                    child_id = child.get('id')
                    response2 = catalog.get_category(category_id=child_id)

                    if response.status_code != 200:
                        catalog.logger.warning(
                            f'Bad request {catalog.current_url}: {catalog.name} category_id: {category_id} part_list: {child_id}')
                        continue

                    data2 = response2.json().get('data')

                    if not data2:
                        catalog.logger.warning(
                            f'Note data in catalog: {catalog.name} category_id: {category_id} part_list: {child_id}')
                        continue

                    children2 = data2[0].get('children')

                    if not children2:
                        catalog.logger.warning(
                            f'No children in data catalog: {catalog.name} category_id: {category_id} part_group_id: {child_id}')
                        continue

                    for index, child2 in enumerate(children2):
                        child2_id = child2.get('id')
                        subcategories[f"{index}_-_{category_id}"] = child2_id
            bar.finish()

            bar = IncrementalBar(f'receive PART_LISTS from subcategories', max=len(subcategories), suffix='%(index)d/%(max)d ')
            for category_data, subcategory_id in subcategories.items():
                bar.next()
                category_id = category_data.split('_-_')[-1]
                response = catalog.get_category(category_id=subcategory_id)

                if response.status_code != 200:
                    catalog.logger.warning(
                        f'Bad request {catalog.current_url}: {catalog.name} category_id: {category_id} subcategory_id: {subcategory_id}')
                    continue

                data = response.json().get('data')

                if not data:
                    catalog.logger.warning(
                        f'No data in catalog: {catalog.name} category_id: {category_id} subcategory_id: {subcategory_id}')
                    continue

                for index, part_list in enumerate(data):
                    part_list_id = part_list.get('id')
                    part_lists[f"{index}_-_{subcategory_id}_-_{category_id}"] = part_list_id
            bar.finish()

            bar = IncrementalBar(f'receive parts from part_lists', max=len(part_lists), suffix='%(index)d/%(max)d ')
            for category_data, part_list_id in part_lists.items():
                bar.next()
                _, subcategory_id, category_id = category_data.split('_-_')
                response = catalog.get_parts(child_id=part_list_id)

                if response.status_code != 200:
                    catalog.logger.warning(
                        f'Bad request {catalog.current_url}: {catalog.name} category_id: {category_id} part_group_id: {subcategory_id} part_list_id: {part_list_id}')
                    continue

                data = response.json().get('data')

                if not data:
                    catalog.logger.warning(
                        f'No Parts in {catalog.name} category_id: {category_id} part_group_id: {subcategory_id} part_list_id: {part_list_id}')
                    continue

                for part in data:
                    part_id = part.get('id')
                    category = catalog.categories[int(category_id)]
                    category.add_part(part_id=part_id)
            bar.finish()
        else:
            catalog.logger.warning(f'No Categories in {catalog.name}')


class TestRopaCatalog(BaseTestCatalog):

    def test_tree(self, catalog):
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

    def test_root_categories(self, catalog):
        instance = self._get_test_instance(catalog)
        instance.test_root_categories(catalog)

    def test_tree(self, catalog):
        instance = self._get_test_instance(catalog)
        instance.test_tree(catalog)

    def test_parts(self, catalog):
        instance = self._get_test_instance(catalog)
        instance.test_parts(catalog)




