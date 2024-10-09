import asyncio
from abc import ABC, abstractmethod
from random import randint
import nest_asyncio
import pytest
from colorama import Fore
from tqdm.asyncio import tqdm
from src.catalog.category import create_category_instance
from src.catalog.part import create_part_instance
from tests.conftest import catalog
from utility import update_spinner
from database import add_parts_list, count_parts_list, count_parts, fetch_all_parts_lists, fetch_parts_lists_batch, \
    fetch_parts

nest_asyncio.apply()


class NoDataException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class CatalogTestUtility:

    async def process_children(self, catalog, category, test_api, t, depth=1):
        if depth > catalog.depth:
            return

        part_list = False

        if depth == catalog.depth and catalog.part_list:
            part_list = True

        async for child in category.fetch_children(test_api=test_api, part_list=part_list):
            if child:
                t.total = t.n * randint(2, 3)
                t.set_postfix_str('...' * randint(1, 2))
                if depth == catalog.depth:
                    t.set_postfix_str(f'{child} from {category}')
                    t.update()
                    await add_parts_list(
                        root_id=child.root_id,
                        parts_list_id=child.id,
                        name=child.name,
                        catalog_name=catalog.name,
                    )

                await self.process_children(catalog=catalog, category=child, test_api=test_api, t=t, depth=depth+1)

    async def process_fetch_parts_from_parts_lists(self, category_id, count, catalog_name):
        if 0 < count < 50:
            parts_lists = await fetch_all_parts_lists(category_id=category_id, catalog_name=catalog_name)
            yield parts_lists

        elif count >= 50:
            batch_size = 50

            for offset in range(0, count, batch_size):
                batch = await fetch_parts_lists_batch(category_id=category_id, batch_size=batch_size, offset=offset, catalog_name=catalog_name)
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
                    t.close()
            else:
                catalog.logger.warning(f'No data in {catalog.current_url} catalog: {catalog}')

    @abstractmethod
    async def test_tree(self, catalog, test_api):
        if catalog.categories:
            categories = list(catalog.categories.values())
            t = tqdm(
                dynamic_ncols=True,
                total=None,
                desc='Process tree traversal and parlists retrieval',
                bar_format="{desc} | {elapsed} | : {bar:30} | {n_fmt} | {postfix}",
            )
            tasks = (asyncio.create_task(self.process_children(catalog=catalog, category=category, test_api=test_api, t=t)) for category in categories)

            try:
                for task in asyncio.as_completed(tasks):
                    await task
            except Exception as error:
                catalog.logger.error(error)
            finally:
                t.total = t.n
                t.close()
        else:
            catalog.logger.warning(f'No Categories in {catalog}')

    async def test_parts(self, catalog, test_api):
        categories = list(catalog.categories.values())

        t = tqdm(
            dynamic_ncols=True,
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
                count = await count_parts_list(category_id=category.id, catalog_name=catalog.name)
                async for parts_lists in self.process_fetch_parts_from_parts_lists(category_id=category.id, count=count, catalog_name=catalog.name):
                    tasks = (asyncio.create_task(_process_batch_fetch_parts(
                        parts_list_data=parts_list_data,
                        obj_catalog=catalog,
                        obj_category=category,
                        progress=t)
                    ) for parts_list_data in parts_lists)

                    for task in asyncio.as_completed(tasks):
                        result = await task

                        if result and test_api:
                            return
        except Exception as error:
            catalog.logger.error(error)
        finally:
            t.total = t.n
            t.close()

        total_parts = 0
        for category in categories:
            total_parts += await count_parts(category_id=category.id, catalog_name=catalog.name)

        t = tqdm(
            dynamic_ncols=True,
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
                parts = await fetch_parts(category_id=category.id, catalog_name=catalog.name)

                if parts:
                    tasks = [asyncio.create_task(_process_validation(
                        part_data=part_data,
                        obj_catalog=catalog,
                        obj_category=category,
                        progress=t,
                        semaphore=semaphore,
                    )) for part_data in parts]

                    for task in asyncio.as_completed(tasks):
                        await task

                    if test_api:
                        return
        except Exception as error:
            catalog.logger.error(error)
        finally:
            t.close()


class TestLemkenCatalog(TestCatalogBase):

    async def test_tree(self, catalog, test_api):
        await super().test_tree(catalog, test_api)


class TestGrimmeCatalog(TestCatalogBase):

    async def test_tree(self, catalog, test_api):
        await super().test_tree(catalog, test_api)


class TestKubotaCatalog(TestCatalogBase):

    async def test_tree(self, catalog, test_api):
        await super().test_tree(catalog, test_api)


class TestClaasCatalog(TestCatalogBase):

    async def test_tree(self, catalog, test_api):
        await super().test_tree(catalog, test_api)


class TestKroneCatalog(TestCatalogBase):

    async def test_tree(self, catalog, test_api):
        await super().test_tree(catalog, test_api)


class TestKvernelandCatalog(TestCatalogBase):

    async def test_tree(self, catalog, test_api):
        await super().test_tree(catalog, test_api)


class TestRopaCatalog(TestCatalogBase):

    async def test_tree(self, catalog, test_api):
        await super().test_tree(catalog, test_api)


class TestJdeereCatalog(TestCatalogBase):

    async def test_tree(self, catalog, test_api):
        await super().test_tree(catalog, test_api)


class TestCatalog:
    """Class wrap for start test"""

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




