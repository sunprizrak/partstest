import os
import logging
import pytest
from src.catalog import Catalog
from datetime import datetime


def pytest_addoption(parser):
    parser.addoption(
        '--catalogs',
        help='Example: catalog1,catalog2',
    )


def pytest_generate_tests(metafunc):
    if 'catalog' in metafunc.fixturenames:
        if 'TestCatalog' in [t.__name__ for t in metafunc.cls.__mro__]:
            option = metafunc.config.getoption('catalogs')
            option_list = option.split(',')
            metafunc.parametrize('catalog', option_list, indirect=True)


@pytest.fixture(scope='module')
def catalog(request):
    catalog_name = request.param
    log_dir = 'logs'

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, f"{catalog_name}_{datetime.now().strftime("%Y-%m-%d")}.log")

    if os.path.exists(log_file):
        os.remove(log_file)

    logger = logging.getLogger(catalog_name)
    logger.setLevel(logging.WARNING)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.WARNING)

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    catalog = Catalog(name=catalog_name)
    catalog.logger = logger

    yield catalog

    logger.removeHandler(file_handler)
    file_handler.close()

    return Catalog(name=catalog_name)