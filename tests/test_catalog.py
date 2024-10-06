import asyncio
from abc import ABC, abstractmethod
from random import randint
import nest_asyncio
from colorama import Fore
from tqdm.asyncio import tqdm
from src.catalog.category import create_category_instance
from src.catalog.part import create_part_instance
from tests.conftest import catalog
from utility import update_spinner
from database import add_parts_list, count_parts_list, count_parts, fetch_all_parts_lists, fetch_parts_lists_batch, \
    fetch_parts, fetch_parts_batch

nest_asyncio.apply()


class NoDataException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class CatalogTestUtility:

    async def process_children(self, category, test_api, t, depth=1, part_list=None):
        if depth > category.catalog.depth:
            return

        async for child in category.fetch_children(test_api=test_api, part_list=part_list):
            if child:
                t.set_postfix_str(f'{child} FROM {category}')
                t.update()
                t.total = t.n * randint(2, 3)
                has_children = True
                if depth == category.catalog.depth:
                    await add_parts_list(
                        root_id=child.root_id,
                        parts_list_id=child.id,
                        name=child.name,
                    )
                await self.process_children(category=child, test_api=test_api, t=t, depth=depth+1)
        return has_children if test_api else None

    async def process_fetch_parts_from_parts_lists(self, category_id, count):
        if 0 < count < 50:
            parts_lists = await fetch_all_parts_lists(category_id=category_id)
            yield parts_lists

        elif count >= 50:
            batch_size = 50

            for offset in range(0, count, batch_size):
                batch = await fetch_parts_lists_batch(category_id=category_id, batch_size=batch_size, offset=offset)
                yield batch


class TestCatalogBase(ABC, CatalogTestUtility):

    async def test_root_categories(self, catalog, test_api):
        spinner = tqdm(total=0, bar_format="{desc}", ncols=30)
        spinner_text = Fore.CYAN + 'Receive categories data'
        spinner_event = asyncio.Event()
        spinner_task = asyncio.create_task(update_spinner(spin=spinner, spin_text=spinner_text, spin_event=spinner_event))

        try:
            resp_json = await catalog.fetch_tree()
        finally:
            spinner_event.set()
            await spinner_task
            spinner.set_description(Fore.CYAN + 'Loaded data categories')
            spinner.close()

        if resp_json:
            data = resp_json.get('data')

            if data:
                t = tqdm(
                    total=len(data),
                    desc='Process root categories',
                    bar_format="{desc} | {elapsed} | : {bar:30} | {n_fmt}/{total_fmt} | {postfix}",
                    postfix=f'Receive categories from {catalog}',
                )

                async def process_category(category_data, catalog):
                    category = await catalog.add_category(data=category_data)
                    t.set_postfix_str(f'{category} from {catalog}')
                    await category.validate(data=category_data)

                tasks = (asyncio.create_task(process_category(category_data=category_data, catalog=catalog)) for category_data in data)
                try:
                    for task in asyncio.as_completed(tasks):
                        await task
                        t.update()
                        await asyncio.sleep(0.1)
                finally:
                    t.set_postfix_str(f"success")
                    t.close()
            else:
                catalog.logger.warning(f'No data in {catalog.current_url} catalog: {catalog}')

    @abstractmethod
    async def test_tree(self, catalog, test_api):
        pass

    async def test_parts(self, catalog, test_api):
        categories = list(catalog.categories.values())

        t = tqdm(
            total=0,
            desc='Process fetch parts',
            bar_format="{desc} | {elapsed} | : {bar:30} | {n_fmt} | {postfix}",
        )

        async def _process_batch_fetch_parts(parts_list_data, obj_catalog, obj_category, progress):
            parts_list_id, name, root_id = parts_list_data

            parts_list = await create_category_instance(
                catalog=obj_catalog,
                category_id=parts_list_id,
                name=name,
                root_id=root_id,
            )
            await parts_list.fetch_parts(category=obj_category, test_api=test_api, t=progress)

        try:
            for category in categories:
                count = await count_parts_list(category_id=category.id)
                async for parts_lists in self.process_fetch_parts_from_parts_lists(category_id=category.id, count=count):
                    tasks = (asyncio.create_task(_process_batch_fetch_parts(
                        parts_list_data=parts_list_data,
                        obj_catalog=catalog,
                        obj_category=category,
                        progress=t)
                    ) for parts_list_data in parts_lists)

                    for task in asyncio.as_completed(tasks):
                        await task

        except Exception as error:
            catalog.logger.error(error)
        finally:
            t.total = t.n
            t.set_postfix_str(f'success')
            t.close()

        total_parts = 0
        for category in categories:
            total_parts += await count_parts(category_id=category.id)

        t = tqdm(
            total=total_parts,
            desc='Process validation details',
            bar_format="{desc} | {elapsed} | : {bar:30} | {n_fmt}/{total_fmt} | {postfix}",
        )

        async def _process_validation(part_data, obj_catalog, obj_category, progress, semaphore):
            async with semaphore:
                detail_id, name, _ = part_data
                part = await create_part_instance(
                    catalog=obj_catalog,
                    category=obj_category,
                    part_id=detail_id,
                    name=name,
                )
                await part.validate(progress=progress)

        semaphore = asyncio.Semaphore(200)

        try:
            for category in categories:
                parts = await fetch_parts(category_id=category.id)

                tasks = [asyncio.create_task(_process_validation(
                    part_data=part_data,
                    obj_catalog=catalog,
                    obj_category=category,
                    progress=t,
                    semaphore=semaphore,
                )) for part_data in parts]

                for task in asyncio.as_completed(tasks):
                    await task
        except Exception as error:
            catalog.logger.error(error)
        finally:
            t.set_postfix_str(f'SUCCESS')
            t.close()


class TestLemkenCatalog(TestCatalogBase):

    async def test_tree(self, catalog, test_api):
        if catalog.categories:
            categories = list(catalog.categories.values())
            t = tqdm(
                total=None,
                desc='Process partslists',
                bar_format="{desc} | {elapsed} | : {bar:30} | {n_fmt} | {postfix}",
            )
            tasks = (asyncio.create_task(self.process_children(category=category, test_api=test_api, t=t)) for category in
                     categories)

            try:
                for task in asyncio.as_completed(tasks):
                    result = await task

                    if result and test_api:
                        for remaining_task in tasks:
                            if remaining_task != task and not remaining_task.done():
                                remaining_task.cancel()
                        break
            except Exception as error:
                catalog.logger.error(error)
            finally:
                t.set_postfix_str('success')
                t.total = t.n
                t.close()
        else:
            catalog.logger.warning(f'No Categories in {catalog}')


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
            catalog.logger.warning(f'No Categories in {catalog}')


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
            catalog.logger.warning(f'No Categories in {catalog}')


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
            catalog.logger.warning(f'No Categories in {catalog}')


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
            catalog.logger.warning(f'No Categories in {catalog}')


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
            catalog.logger.warning(f'No Categories in {catalog}')


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
            catalog.logger.warning(f'No Categories in {catalog}')


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
            catalog.logger.warning(f'No Categories in {catalog}')


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

    async def test_root_categories(self, catalog, test_api):
        instance = self._get_test_instance(catalog)
        await instance.test_root_categories(catalog, test_api)

    async def test_tree(self, catalog, test_api):
        instance = self._get_test_instance(catalog)
        await instance.test_tree(catalog, test_api)

    async def test_parts(self, catalog, test_api):
        instance = self._get_test_instance(catalog)
        await instance.test_parts(catalog, test_api)




