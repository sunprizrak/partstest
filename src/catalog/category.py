import asyncio
import time
from abc import ABC, abstractmethod
from random import randint

from tqdm import tqdm
from database import add_detail as db_add_detail


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

    async def process_save_part(self, data, t):
        part_id = data.get('id')
        name = data.get(self.name_label_part)

        await db_add_detail(
            detail_id=part_id,
            name=name,
            category_id=self.root_id,
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

            tasks = (self.process_save_part(data=part_data, t=t) for part_data in data)

            for task in asyncio.as_completed(tasks):
                await task

    @abstractmethod
    async def fetch_children(self, test_api, part_list):
        data_json = await self.catalog.fetch_category(category_id=self.id)

        if data_json:
            category_data = data_json.get('data')

            if not category_data:
                self.catalog.logger.warning(
                    f'Note data in {self.catalog}/{self}')
                yield False

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

            async def fetch_children_data(category):
                children_data = category.get('children')
                if not children_data:
                    self.catalog.logger.warning(f'No children in data {self.catalog}/{self}')

                return children_data

            category_tasks = (fetch_children_data(category=data) for data in category_data)

            for ctr_task in asyncio.as_completed(category_tasks):
                children = await ctr_task

                if children:
                    if test_api:
                        children = children[:1]

                    children_tasks = (fetch_child_data(child_data=child_data) for child_data in children)
                    for child_task in asyncio.as_completed(children_tasks):
                        child = await child_task
                        yield child
            else:
                yield False

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
        await super().validate(data=data)

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

    def validate(self, data: dict):
        return super().validate(data=data)

    def fetch_children(self, test_api, part_list=None):
        return super().get_children(test_api, part_list)

    def get_parts(self, test_api):
        return super().get_parts(test_api)


class GrimmeCategory(Category):
    def __init__(self, *args, **kwargs):
        super(GrimmeCategory, self).__init__(*args, **kwargs)
        self.modifications = []
        self.validation_fields = {
            'id', 'label', 'parent_id', 'linkType',
            'children', 'created_at', 'updated_at',
        }

    def get_children(self, test_api, part_list=None):
        response = self.catalog.get_category(category_id=self.id)

        if response.status_code != 200:
            self.catalog.logger.warning(
                f'Bad request {self.catalog.current_url} catalog: {self.catalog.name} category_name: {self.name} category_id: {self.id}')
            return False

        children = response.json().get('data')

        if not children:
            self.catalog.logger.warning(
                f'No children in data catalog: {self.catalog.name} category_name: {self.name} category_id: {self.id}')
            return False

        if test_api:
            children = children[:1]

        for child_data in children:
            child_id = child_data.get('id')
            child_name = child_data.get(self.catalog.name_label_category)

            kwargs_dict = {
                'child_id': child_id,
                'child_name': child_name,
            }

            if hasattr(self, 'root_id'):
                kwargs_dict['root_id'] = self.root_id
            else:
                kwargs_dict['root_id'] = self.id

            self.add_children(**kwargs_dict)
        return self.children

    def get_parts(self, test_api):
        with tqdm(
                total=len(self.part_lists),
                bar_format="{l_bar}{bar:30} | {n_fmt}/{total_fmt} {postfix}",
                postfix='') as t:
            for part_list in self.part_lists:
                t.set_postfix_str(f"details from {part_list}")
                t.update()

                response = self.catalog.get_category(category_id=part_list.id)

                if response.status_code != 200:
                    self.catalog.logger.warning(
                        f'Bad request {self.catalog.current_url} catalog: {self.catalog.name} category_name: {self.name} category_id: {self.id} part_list_id: {part_list.id} ')
                    continue

                data = response.json().get('data')

                if not data:
                    self.catalog.logger.warning(
                        f'No Parts in {self.catalog.name} category_name: {self.name} category_id: {self.id} part_list_id: {part_list.id}')
                    continue

                if test_api:
                    data = data[:1]

                for part in data:
                    part_id = part.get('id')
                    part_name = part.get(self.name_label_part)
                    self.add_part(part_id=part_id, name=part_name)

                if test_api:
                    time.sleep(0.2)
            t.set_postfix_str('Details received')

    def validate(self, data: dict):
        return super().validate(data=data)


class KroneCategory(Category):

    def __init__(self, *args, **kwargs):
        super(KroneCategory, self).__init__(*args, **kwargs)
        self.validation_fields = {
            'id', 'name', 'parent_id', 'link_type', 'children',
            'created_at', 'updated_at', 'position', 'description',
            'remark', 'imageFields',
        }
        self.validation_image_fields = {'name', 's3'}

    def validate(self, data: dict):
        return super().validate(data=data)

    def get_children(self, test_api, part_list=None):
        return super().get_children(test_api, part_list)

    def get_parts(self, test_api):
        return super().get_parts(test_api)


class KvernelandCategory(Category):
    def __init__(self, *args, **kwargs):
        super(KvernelandCategory, self).__init__(*args, **kwargs)
        self.validation_fields = {
            'id', 'name', 'parent_id', 'link_type', 'children',
            'created_at', 'updated_at', 'position', 'description',
            'remark', 'imageFields',
        }
        self.validation_image_fields = {'name', 's3'}

    def validate(self, data: dict):
        return super().validate(data=data)

    def get_parts(self, test_api):
        return super().get_parts(test_api)

    def get_children(self, test_api, part_list=None):
        return super().get_children(test_api, part_list)


class JdeereCategory(Category):

    def __init__(self, *args, **kwargs):
        super(JdeereCategory, self).__init__(*args, **kwargs)
        self.validation_fields = {
            'id', 'name', 'parent_id', 'link_type', 'children',
            'created_at', 'updated_at', 'position', 'description',
            'remark', 'imageFields',
        }
        self.validation_image_fields = {'name', 's3'}

    def validate(self, data: dict):
        return super().validate(data=data)

    def get_parts(self, test_api):
        return super().get_parts(test_api)

    def get_children(self, test_api, part_list=None):
        return super().get_children(test_api, part_list)


class ClaasCategory(Category):

    def __init__(self, *args, **kwargs):
        super(ClaasCategory, self).__init__(*args, **kwargs)
        self.validation_fields = {
            'id', 'name', 'parent_id', 'link_type', 'children',
            'created_at', 'updated_at', 'position', 'description',
            'remark', 'imageFields',
        }
        self.validation_image_fields = {'name', 's3'}

    def validate(self, data: dict):
        return super().validate(data=data)

    def get_children(self, test_api, part_list=None):
        return super().get_children(test_api, part_list)

    def get_parts(self, test_api):
        return super().get_parts(test_api)


class RopaCategory(Category):
    def __init__(self, *args, **kwargs):
        super(RopaCategory, self).__init__(*args, **kwargs)
        self.validation_fields = {
            'id', 'name', 'parent_id', 'link_type', 'children',
            'created_at', 'updated_at', 'description', 'imageFields',
        }
        self.validation_image_fields = {'name', 's3'}

    def validate(self, data: dict):
        return super().validate(data=data)

    def get_children(self, test_api, part_list=None):
        return super().get_children(test_api, part_list)

    def get_parts(self, test_api):
        return super().get_parts(test_api)


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
