import pytest
from src.catalog import Catalog


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
    return Catalog(name=catalog_name)