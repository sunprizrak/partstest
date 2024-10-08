import asyncio
import time
from abc import ABC, abstractmethod
from random import randint

from tqdm import tqdm
from database import add_detail as db_add_detail
from tests.conftest import catalog


class Category(ABC):
    name_label_part = 'name'

    def __init__(self, *args, **kwargs):
        self.catalog = kwargs.get('catalog')
        if kwargs.get('root_id'):
            self.root_id = kwargs.get('root_id')
        self.id = kwargs.get('category_id')
        self.name = kwargs.get('name')
        self.validation_fields = set()
        self.validation_image_fields = set()

    async def process_save_part(self, data, t, catalog_name):
        part_id = data.get('id')
        name = data.get(self.name_label_part)

        await db_add_detail(
            detail_id=part_id,
            name=name,
            category_id=self.root_id,
            catalog_name=catalog_name,
        )

        t.set_postfix_str(f'{name} {part_id} FROM {self}')
        t.update()
        t.total = t.n * randint(2, 3)

    @abstractmethod
    async def fetch_parts(self, category, test_api, t):
        data_json = await self.catalog.fetch_parts(part_list_id=self.id)

        if data_json:
            data = data_json.get('data')

            if not data:
                self.catalog.logger.warning(f'No details in {self.catalog}/{category}/{self}')
                return

            if test_api:
                data = data[:1]

            tasks = (self.process_save_part(data=part_data, t=t, catalog_name=self.catalog.name) for part_data in data)

            for task in asyncio.as_completed(tasks):
                await task

    @abstractmethod
    async def fetch_children(self, test_api, part_list):
        data_json = await self.catalog.fetch_category(category_id=self.id)

        if data_json:
            category_data = data_json.get('data')

            if not category_data:
                self.catalog.logger.warning(
                    f'No data in {self.catalog}/{self}')
                return

            if test_api:
                category_data = category_data[:1]

            async def fetch_child_data(child_data):
                if child_data:
                    child_id = child_data.get('id')
                    child_name = child_data.get(self.catalog.name_label_category)

                    if hasattr(self, 'root_id'):
                        root_id = self.root_id
                    else:
                        root_id = self.id

                    obj = await create_category_instance(
                        catalog=self.catalog,
                        category_id=child_id,
                        name=child_name,
                        root_id=root_id,
                    )
                    return obj

            async def fetch_children_data(data):
                if part_list:
                    children = data
                else:
                    children = data.get('children')
                if not children:
                    self.catalog.logger.warning(f'No children {self.catalog}/{self}')

                return children

            if test_api and part_list:
                category_data = category_data[:1]

            category_tasks = (fetch_children_data(data=data) for data in category_data)

            for ctr_task in asyncio.as_completed(category_tasks):
                result = await ctr_task

                if result:
                    if part_list:
                        child = await fetch_child_data(child_data=result)
                        if child:
                            yield child
                    else:
                        if test_api:
                            result = result[:1]

                        children_tasks = (fetch_child_data(child_data=child_data) for child_data in result)
                        for child_task in asyncio.as_completed(children_tasks):
                            child = await child_task
                            if child:
                                yield child
        else:
            return

    @abstractmethod
    async def validate(self, data: dict):
        image_fields = data.get('imageFields')

        missing_fields = self.validation_fields - data.keys()

        if len(missing_fields) > 0:
            self.catalog.logger.warning(
                f"Missing fields {missing_fields} in {self.catalog}/{self}")

        if image_fields:
            missing_fields = self.validation_image_fields - image_fields.keys()

            if len(missing_fields) > 0:
                self.catalog.logger.warning(
                    f"Missing fields  {missing_fields} in imageFields => in {self.catalog}/{self}")

    def __str__(self):
        return f"{self.name} id:{self.id}"

    def __repr__(self):
        return f"{self.name} id:{self.id}"


class LemkenCategory(Category):

    def __init__(self, *args, **kwargs):
        super(LemkenCategory, self).__init__(*args, **kwargs)
        self.validation_fields = {
            'id', 'name', 'parent_id', 'link_type', 'children',
            'created_at', 'updated_at', 'position', 'description',
            'remark', 'imageFields',
        }
        self.validation_image_fields = {'name', 's3'}

    async def validate(self, data: dict):
        await super().validate(data)

    async def fetch_children(self, test_api, part_list):
        async for child in super().fetch_children(test_api, part_list):
            yield child

    async def fetch_parts(self, category, test_api, t):
        await super().fetch_parts(category, test_api, t)


class KubotaCategory(Category):

    def __init__(self, *args, **kwargs):
        super(KubotaCategory, self).__init__(*args, **kwargs)
        self.validation_fields = {
            'id', 'name', 'parent_id', 'link_type', 'children',
            'created_at', 'updated_at', 'position', 'description',
            'remark', 'imageFields',
        }
        self.validation_image_fields = {'name', 's3'}

    async def validate(self, data: dict):
        await super().validate(data)

    async def fetch_children(self, test_api, part_list):
        async for child in super().fetch_children(test_api, part_list):
            yield child

    async def fetch_parts(self, category, test_api, t):
        await super().fetch_parts(category, test_api, t)


class GrimmeCategory(Category):

    def __init__(self, *args, **kwargs):
        super(GrimmeCategory, self).__init__(*args, **kwargs)
        self.modifications = []
        self.validation_fields = {
            'id', 'label', 'parent_id', 'linkType',
            'children', 'created_at', 'updated_at',
        }

    async def validate(self, data):
        await super().validate(data)

    async def fetch_children(self, test_api, part_list):
        data_json = await self.catalog.fetch_category(category_id=self.id)

        if data_json:
            children = data_json.get('data')

            if not children:
                self.catalog.logger.warning(
                    f'No children in data: {self.catalog.name}/{self}')
                return

            if test_api:
                children = children[:1]

            async def fetch_child_data(child_data):
                if child_data:
                    child_id = child_data.get('id')
                    child_name = child_data.get(self.catalog.name_label_category)

                    if hasattr(self, 'root_id'):
                        root_id = self.root_id
                    else:
                        root_id = self.id

                    obj = await create_category_instance(
                        catalog=self.catalog,
                        category_id=child_id,
                        name=child_name,
                        root_id=root_id,
                    )
                    return obj

            children_tasks = (fetch_child_data(child_data=child_data) for child_data in children)
            for child_task in asyncio.as_completed(children_tasks):
                child = await child_task
                if child:
                    yield child
        else:
            return

    async def fetch_parts(self, category, test_api, t):
        data_json = await self.catalog.fetch_category(category_id=self.id)

        if data_json:
            data = data_json.get('data')

            if not data:
                self.catalog.logger.warning(f'No details in {self.catalog}/{category}/{self}')
                return

            if test_api:
                data = data[:1]

            tasks = (self.process_save_part(data=part_data, t=t) for part_data in data)

            for task in asyncio.as_completed(tasks):
                await task


class KroneCategory(Category):

    def __init__(self, *args, **kwargs):
        super(KroneCategory, self).__init__(*args, **kwargs)
        self.validation_fields = {
            'id', 'name', 'parent_id', 'link_type', 'children',
            'created_at', 'updated_at', 'position', 'description',
            'remark', 'imageFields',
        }
        self.validation_image_fields = {'name', 's3'}

    async def validate(self, data: dict):
        await super().validate(data)

    async def fetch_children(self, test_api, part_list):
        async for child in super().fetch_children(test_api, part_list):
            yield child

    async def fetch_parts(self, category, test_api, t):
        await super().fetch_parts(category, test_api, t)


class KvernelandCategory(Category):
    def __init__(self, *args, **kwargs):
        super(KvernelandCategory, self).__init__(*args, **kwargs)
        self.validation_fields = {
            'id', 'name', 'parent_id', 'link_type', 'children',
            'created_at', 'updated_at', 'position', 'description',
            'remark', 'imageFields',
        }
        self.validation_image_fields = {'name', 's3'}

    async def validate(self, data):
        await super().validate(data)

    async def fetch_children(self, test_api, part_list):
        async for child in super().fetch_children(test_api, part_list):
            yield child

    async def fetch_parts(self, category, test_api, t):
        await super().fetch_parts(category, test_api, t)


class JdeereCategory(Category):

    def __init__(self, *args, **kwargs):
        super(JdeereCategory, self).__init__(*args, **kwargs)
        self.validation_fields = {
            'id', 'name', 'parent_id', 'link_type', 'children',
            'created_at', 'updated_at', 'position', 'description',
            'remark', 'imageFields',
        }
        self.validation_image_fields = {'name', 's3'}

    async def validate(self, data: dict):
        await super().validate(data)

    async def fetch_children(self, test_api, part_list):
        async for child in super().fetch_children(test_api, part_list):
            yield child

    async def fetch_parts(self, category, test_api, t):
        await super().fetch_parts(category, test_api, t)


class ClaasCategory(Category):

    def __init__(self, *args, **kwargs):
        super(ClaasCategory, self).__init__(*args, **kwargs)
        self.validation_fields = {
            'id', 'name', 'parent_id', 'link_type', 'children',
            'created_at', 'updated_at', 'position', 'description',
            'remark', 'imageFields',
        }
        self.validation_image_fields = {'name', 's3'}

    async def validate(self, data):
        await super().validate(data)

    async def fetch_children(self, test_api, part_list):
        async for child in super().fetch_children(test_api, part_list):
            yield child

    async def fetch_parts(self, category, test_api, t):
        await super().fetch_parts(category, test_api, t)


class RopaCategory(Category):
    def __init__(self, *args, **kwargs):
        super(RopaCategory, self).__init__(*args, **kwargs)
        self.validation_fields = {
            'id', 'name', 'parent_id', 'link_type', 'children',
            'created_at', 'updated_at', 'description', 'imageFields',
        }
        self.validation_image_fields = {'name', 's3'}

    async def validate(self, data):
        await super().validate(data)

    async def fetch_children(self, test_api, part_list):
        async for child in super().fetch_children(test_api, part_list):
            yield child

    async def fetch_parts(self, category, test_api, t):
        await super().fetch_parts(category, test_api, t)


async def create_category_instance(catalog, category_id, name, root_id=None):
    cls = globals().get(f"{catalog.name.capitalize()}Category")
    cleaned_name = name.strip().replace('\n', '')
    if cls is None:
        raise ValueError(f"Class {catalog.name.capitalize()}Category is not defined.")

    if root_id:
        return cls(catalog=catalog, category_id=category_id, name=cleaned_name, root_id=root_id)
    else:
        return cls(catalog=catalog, category_id=category_id, name=cleaned_name)


if __name__ == '__main__':
    pass
