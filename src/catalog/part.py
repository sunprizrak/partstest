from abc import ABC, abstractmethod


class Part(ABC):

    def __init__(self, catalog, category, part_id):
        self.catalog = catalog
        self.category = category
        self.id = part_id
        self.validation_fields = set()
        self.validation_image_fields = set()

    @abstractmethod
    def validate(self, data: dict):
        pass

    def __str__(self):
        return f"detail id:{self.id}"

    def __repr__(self):
        return f"detail id:{self.id}"


class LemkenPart(Part):

    def __init__(self, catalog, category, part_id):
        super(LemkenPart, self).__init__(catalog, category, part_id)
        self.validation_fields = {
            'id', 'name', 'link_type', 'quantity',
            'part_number', 'position', 'dimension',
            'imageFields', 'created_at', 'updated_at',
        }
        self.validation_image_fields = {'name', 's3'}
        self.validation_category_fields = {'id'}

    def validate(self, data: dict):
        image_fields = data.get('imageFields')
        part_category = data.get('category')

        missing_fields = self.validation_fields - data.keys()

        if len(missing_fields) > 0:
            self.catalog.logger.warning(
                f"Missing fields {missing_fields} in catalog: {self.catalog.name} category_id: {self.category.id} part_id: {self.id}")

        if image_fields:
            missing_fields = self.validation_image_fields - image_fields.keys()

            if len(missing_fields) > 0:
                self.catalog.logger.warning(
                    f"Missing fields  {missing_fields} in imageFields => in catalog: {self.catalog.name} category_id: {self.category.id} part_id: {self.id}")

        if part_category:
            missing_fields = self.validation_category_fields - part_category.keys()

            if len(missing_fields) > 0:
                self.catalog.logger.warning(f'Missing fields {missing_fields} in {self.catalog.name} category_id: {self.category.id} part_id: {self.id}')
        else:
            self.catalog.logger.warning(f'No part_category in {self.catalog.name} category_id: {self.category.id} part_id: {self.id}')


class KubotaPart(Part):
    def __init__(self, catalog, category, part_id):
        super(KubotaPart, self).__init__(catalog, category, part_id)
        self.validation_fields = {
            'id', 'name', 'link_type', 'quantity',
            'part_number', 'position', 'dimension',
            'imageFields', 'created_at', 'updated_at',
        }
        self.validation_image_fields = {'name', 's3'}
        self.validation_category_fields = {'id'}

    def validate(self, data: dict):
        image_fields = data.get('imageFields')
        part_category = data.get('category')

        missing_fields = self.validation_fields - data.keys()

        if len(missing_fields) > 0:
            self.catalog.logger.warning(
                f"Missing fields {missing_fields} in catalog: {self.catalog.name} category_id: {self.category.id} part_id: {self.id}")

        if image_fields:
            missing_fields = self.validation_image_fields - image_fields.keys()

            if len(missing_fields) > 0:
                self.catalog.logger.warning(
                    f"Missing fields  {missing_fields} in imageFields => in catalog: {self.catalog.name} category_id: {self.category.id} part_id: {self.id}")

        if part_category:
            missing_fields = self.validation_category_fields - part_category.keys()

            if len(missing_fields) > 0:
                self.catalog.logger.warning(f'Missing fields {missing_fields} in {self.catalog.name} category_id: {self.category.id} part_id: {self.id}')
        else:
            self.catalog.logger.warning(f'No part_category in {self.catalog.name} category_id: {self.category.id} part_id: {self.id}')


class ClaasPart(Part):
    def __init__(self, catalog, category, part_id):
        super(ClaasPart, self).__init__(catalog, category, part_id)
        self.validation_fields = {
            'id', 'name', 'link_type', 'quantity',
            'part_number', 'position', 'dimension',
            'imageFields', 'created_at', 'updated_at',
        }
        self.validation_image_fields = {'name', 's3'}
        self.validation_category_fields = {'id'}

    def validate(self, data: dict):
        image_fields = data.get('imageFields')
        part_category = data.get('category')

        missing_fields = self.validation_fields - data.keys()

        if len(missing_fields) > 0:
            self.catalog.logger.warning(
                f"Missing fields {missing_fields} in catalog: {self.catalog.name} category_id: {self.category.id} part_id: {self.id}")

        if image_fields:
            missing_fields = self.validation_image_fields - image_fields.keys()

            if len(missing_fields) > 0:
                self.catalog.logger.warning(
                    f"Missing fields  {missing_fields} in imageFields => in catalog: {self.catalog.name} category_id: {self.category.id} part_id: {self.id}")

        if part_category:
            missing_fields = self.validation_category_fields - part_category.keys()

            if len(missing_fields) > 0:
                self.catalog.logger.warning(
                    f'Missing fields {missing_fields} in {self.catalog.name} category_id: {self.category.id} part_id: {self.id}')
        else:
            self.catalog.logger.warning(
                f'No part_category in {self.catalog.name} category_id: {self.category.id} part_id: {self.id}')


class RopaPart(Part):

    def __init__(self, catalog, category, part_id):
        super(RopaPart, self).__init__(catalog, category, part_id)
        self.validation_fields = {
            'id', 'name', 'link_type', 'quantity',
            'part_number', 'position', 'dimension',
            'imageFields', 'created_at', 'updated_at',
        }
        self.validation_image_fields = {'name', 's3'}
        self.validation_category_fields = {'id'}

    def validate(self, data: dict):
        image_fields = data.get('imageFields')
        part_category = data.get('category')

        missing_fields = self.validation_fields - data.keys()

        if len(missing_fields) > 0:
            self.catalog.logger.warning(
                f"Missing fields {missing_fields} in catalog: {self.catalog.name} category_id: {self.category.id} part_id: {self.id}")

        if image_fields:
            missing_fields = self.validation_image_fields - image_fields.keys()

            if len(missing_fields) > 0:
                self.catalog.logger.warning(
                    f"Missing fields  {missing_fields} in imageFields => in catalog: {self.catalog.name} category_id: {self.category.id} part_id: {self.id}")

        if part_category:
            missing_fields = self.validation_category_fields - part_category.keys()

            if len(missing_fields) > 0:
                self.catalog.logger.warning(
                    f'Missing fields {missing_fields} in {self.catalog.name} category_id: {self.category.id} part_id: {self.id}')
        else:
            self.catalog.logger.warning(
                f'No part_category in {self.catalog.name} category_id: {self.category.id} part_id: {self.id}')


class GrimmePart(Part):

    def __init__(self, catalog, category, part_id):
        super(GrimmePart, self).__init__(catalog, category, part_id)
        self.validation_fields = {
            'id', 'name', 'link_type', 'quantity',
            'part_number', 'position', 'dimension',
            'imageFields', 'created_at', 'updated_at',
        }
        self.validation_image_fields = {'name', 's3'}
        self.validation_category_fields = {'id'}

    def validate(self, data: dict):
        image_fields = data.get('imageFields')
        part_category = data.get('category')

        missing_fields = self.validation_fields - data.keys()

        if len(missing_fields) > 0:
            self.catalog.logger.warning(
                f"Missing fields {missing_fields} in catalog: {self.catalog.name} category_id: {self.category.id} part_id: {self.id}")

        if image_fields:
            missing_fields = self.validation_image_fields - image_fields.keys()

            if len(missing_fields) > 0:
                self.catalog.logger.warning(
                    f"Missing fields  {missing_fields} in imageFields => in catalog: {self.catalog.name} category_id: {self.category.id} part_id: {self.id}")

        if part_category:
            missing_fields = self.validation_category_fields - part_category.keys()

            if len(missing_fields) > 0:
                self.catalog.logger.warning(
                    f'Missing fields {missing_fields} in {self.catalog.name} category_id: {self.category.id} part_id: {self.id}')
        else:
            self.catalog.logger.warning(
                f'No part_category in {self.catalog.name} category_id: {self.category.id} part_id: {self.id}')


class KronePart(Part):
    def __init__(self, catalog, category, part_id):
        super(KronePart, self).__init__(catalog, category, part_id)
        self.validation_fields = {
            'id', 'name', 'link_type', 'quantity',
            'part_number', 'position', 'dimension',
            'imageFields', 'created_at', 'updated_at',
        }
        self.validation_image_fields = {'name', 's3'}
        self.validation_category_fields = {'id'}

    def validate(self, data: dict):
        image_fields = data.get('imageFields')
        part_category = data.get('category')

        missing_fields = self.validation_fields - data.keys()

        if len(missing_fields) > 0:
            self.catalog.logger.warning(
                f"Missing fields {missing_fields} in catalog: {self.catalog.name} category_id: {self.category.id} part_id: {self.id}")

        if image_fields:
            missing_fields = self.validation_image_fields - image_fields.keys()

            if len(missing_fields) > 0:
                self.catalog.logger.warning(
                    f"Missing fields  {missing_fields} in imageFields => in catalog: {self.catalog.name} category_id: {self.category.id} part_id: {self.id}")

        if part_category:
            missing_fields = self.validation_category_fields - part_category.keys()

            if len(missing_fields) > 0:
                self.catalog.logger.warning(
                    f'Missing fields {missing_fields} in {self.catalog.name} category_id: {self.category.id} part_id: {self.id}')
        else:
            self.catalog.logger.warning(
                f'No part_category in {self.catalog.name} category_id: {self.category.id} part_id: {self.id}')


class KvernelandPart(Part):
    def __init__(self, catalog, category, part_id):
        super(KvernelandPart, self).__init__(catalog, category, part_id)
        self.validation_fields = {
            'id', 'name', 'link_type', 'quantity',
            'part_number', 'position', 'dimension',
            'imageFields', 'created_at', 'updated_at',
        }
        self.validation_image_fields = {'name', 's3'}
        self.validation_category_fields = {'id'}

    def validate(self, data: dict):
        image_fields = data.get('imageFields')
        part_category = data.get('category')

        missing_fields = self.validation_fields - data.keys()

        if len(missing_fields) > 0:
            self.catalog.logger.warning(
                f"Missing fields {missing_fields} in catalog: {self.catalog.name} category_id: {self.category.id} part_id: {self.id}")

        if image_fields:
            missing_fields = self.validation_image_fields - image_fields.keys()

            if len(missing_fields) > 0:
                self.catalog.logger.warning(
                    f"Missing fields  {missing_fields} in imageFields => in catalog: {self.catalog.name} category_id: {self.category.id} part_id: {self.id}")

        if part_category:
            missing_fields = self.validation_category_fields - part_category.keys()

            if len(missing_fields) > 0:
                self.catalog.logger.warning(
                    f'Missing fields {missing_fields} in {self.catalog.name} category_id: {self.category.id} part_id: {self.id}')
        else:
            self.catalog.logger.warning(
                f'No part_category in {self.catalog.name} category_id: {self.category.id} part_id: {self.id}')


class JdeerePart(Part):
    def __init__(self, catalog, category, part_id):
        super(JdeerePart, self).__init__(catalog, category, part_id)
        self.validation_fields = {
            'id', 'name', 'link_type', 'quantity',
            'part_number', 'position', 'dimension',
            'imageFields', 'created_at', 'updated_at',
        }
        self.validation_image_fields = {'name', 's3'}
        self.validation_category_fields = {'id'}

    def validate(self, data: dict):
        image_fields = data.get('imageFields')
        part_category = data.get('category')

        missing_fields = self.validation_fields - data.keys()

        if len(missing_fields) > 0:
            self.catalog.logger.warning(
                f"Missing fields {missing_fields} in catalog: {self.catalog.name} category_id: {self.category.id} part_id: {self.id}")

        if image_fields:
            missing_fields = self.validation_image_fields - image_fields.keys()

            if len(missing_fields) > 0:
                self.catalog.logger.warning(
                    f"Missing fields  {missing_fields} in imageFields => in catalog: {self.catalog.name} category_id: {self.category.id} part_id: {self.id}")

        if part_category:
            missing_fields = self.validation_category_fields - part_category.keys()

            if len(missing_fields) > 0:
                self.catalog.logger.warning(
                    f'Missing fields {missing_fields} in {self.catalog.name} category_id: {self.category.id} part_id: {self.id}')
        else:
            self.catalog.logger.warning(
                f'No part_category in {self.catalog.name} category_id: {self.category.id} part_id: {self.id}')


def create_part_instance(catalog, category, part_id):
    cls = globals().get(f"{catalog.name.capitalize()}Part")
    if cls is None:
        raise ValueError(f"Class {catalog.name.capitalize()}Part is not defined.")
    return cls(catalog, category, part_id)