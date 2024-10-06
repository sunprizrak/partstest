import asyncio
from abc import ABC, abstractmethod


class Part(ABC):

    def __init__(self, *args, **kwargs):
        self.catalog = kwargs.get('catalog')
        self.category = kwargs.get('category')
        self.id = kwargs.get('part_id')
        self.name = kwargs.get('name')
        self.validation_fields = set()
        self.validation_image_fields = set()
        self.validation_category_fields = set()

    @abstractmethod
    async def validate(self, progress):
        progress.set_postfix_str(f'{self}')
        progress.update()

        data_json = await self.catalog.fetch_part(part_id=self.id)

        if data_json:
            data = data_json.get('data')

            if data:
                image_fields = data.get('imageFields')
                part_category = data.get('category')

                missing_fields = self.validation_fields - data.keys()

                if len(missing_fields) > 0:
                    self.catalog.logger.warning(
                        f"Missing fields {missing_fields} in {self.catalog}/{self.category}/{self}")

                if image_fields:
                    missing_fields = self.validation_image_fields - image_fields.keys()

                    if len(missing_fields) > 0:
                        self.catalog.logger.warning(
                            f"Missing fields  {missing_fields} in imageFields => {self.catalog}/{self.category}/{self}")

                if part_category:
                    missing_fields = self.validation_category_fields - part_category.keys()

                    if len(missing_fields) > 0:
                        self.catalog.logger.warning(
                            f'Missing fields {missing_fields} in {self.catalog}/{self.category}/{self}')
                else:
                    self.catalog.logger.warning(f'No part_category in {self.catalog}/{self.category}/{self}')

    def __str__(self):
        return f"{self.name} id:{self.id}"

    def __repr__(self):
        return f"{self.name} id:{self.id}"


class LemkenPart(Part):

    def __init__(self, *args, **kwargs):
        super(LemkenPart, self).__init__(*args, **kwargs)
        self.validation_fields = {
            'id', 'name', 'link_type', 'quantity',
            'part_number', 'position', 'dimension',
            'imageFields', 'created_at', 'updated_at',
        }
        self.validation_image_fields = {'name', 's3'}
        self.validation_category_fields = {'id'}

    async def validate(self, progress):
        await super().validate(progress)


class KubotaPart(Part):
    def __init__(self, *args, **kwargs):
        super(KubotaPart, self).__init__(*args, **kwargs)
        self.validation_fields = {
            'id', 'name', 'link_type', 'quantity',
            'part_number', 'position', 'dimension',
            'imageFields', 'created_at', 'updated_at',
        }
        self.validation_image_fields = {'name', 's3'}
        self.validation_category_fields = {'id'}

    async def validate(self, data: dict):
        await super().validate(data=data)


class ClaasPart(Part):
    def __init__(self, *args, **kwargs):
        super(ClaasPart, self).__init__(*args, **kwargs)
        self.validation_fields = {
            'id', 'name', 'link_type', 'quantity',
            'part_number', 'position', 'dimension',
            'imageFields', 'created_at', 'updated_at',
        }
        self.validation_image_fields = {'name', 's3'}
        self.validation_category_fields = {'id'}

    async def validate(self, data: dict):
        await super().validate(data=data)


class RopaPart(Part):

    def __init__(self, *args, **kwargs):
        super(RopaPart, self).__init__(*args, **kwargs)
        self.validation_fields = {
            'id', 'name', 'link_type', 'quantity',
            'part_number', 'position', 'imageFields',
            'created_at', 'updated_at',
        }
        self.validation_image_fields = {'name', 's3'}
        self.validation_category_fields = {'id'}

    async def validate(self, data: dict):
        await super().validate(data=data)


class GrimmePart(Part):

    def __init__(self, *args, **kwargs):
        super(GrimmePart, self).__init__(*args, **kwargs)
        self.validation_fields = {
            'id', 'name', 'link_type', 'quantity',
            'partNumber', 'position', 'created_at',
            'updated_at',
        }

    async def validate(self, data: dict):
        await super().validate(data=data)


class KronePart(Part):
    def __init__(self, *args, **kwargs):
        super(KronePart, self).__init__(*args, **kwargs)
        self.validation_fields = {
            'id', 'name', 'link_type', 'quantity',
            'part_number', 'position', 'dimension',
            'imageFields', 'created_at', 'updated_at',
        }
        self.validation_image_fields = {'name', 's3'}
        self.validation_category_fields = {'id'}

    async def validate(self, data: dict):
        await super().validate(data=data)


class KvernelandPart(Part):
    def __init__(self, *args, **kwargs):
        super(KvernelandPart, self).__init__(*args, **kwargs)
        self.validation_fields = {
            'id', 'name', 'link_type', 'quantity',
            'part_number', 'position', 'dimension',
            'imageFields', 'created_at', 'updated_at',
        }
        self.validation_image_fields = {'name', 's3'}
        self.validation_category_fields = {'id'}

    async def validate(self, data: dict):
        await super().validate(data=data)


class JdeerePart(Part):
    def __init__(self, *args, **kwargs):
        super(JdeerePart, self).__init__(*args, **kwargs)
        self.validation_fields = {
            'id', 'name', 'link_type', 'quantity',
            'part_number', 'position', 's3_image_name',
            'created_at', 'updated_at',
        }
        self.validation_category_fields = {'id'}

    async def validate(self, data: dict):
        await super().validate(data=data)


async def create_part_instance(catalog, category, part_id, name):
    cls = globals().get(f"{catalog.name.capitalize()}Part")
    if cls is None:
        raise ValueError(f"Class {catalog.name.capitalize()}Part is not defined.")
    return cls(catalog=catalog, category=category, part_id=part_id, name=name)