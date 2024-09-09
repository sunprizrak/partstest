import pytest
from src.catalog.catalog import create_catalog_instance


def pytest_addoption(parser):
    parser.addoption(
        '--catalogs',
        help='Example: catalog1,catalog2',
    )
    parser.addoption(
        '--test_api',
        action='store_true',  # Если это просто флаг, который включается
        help='Enable API testing',
    )


def pytest_generate_tests(metafunc):
    if 'catalog' in metafunc.fixturenames:
        if 'TestCatalog' in [t.__name__ for t in metafunc.cls.__mro__]:
            option = metafunc.config.getoption('catalogs')
            option_list = option.split(',')
            metafunc.parametrize('catalog', option_list, indirect=True)

    if 'test_api' in metafunc.fixturenames:
        test_api_option = metafunc.config.getoption('test_api')
        metafunc.parametrize('test_api', [test_api_option])


@pytest.fixture(scope='module')
def catalog(request):
    catalog_name = request.param
    catalog = create_catalog_instance(catalog_name=catalog_name)
    return catalog


@pytest.fixture(scope='module')
def test_api(request):
    return request.param  # Вернет True или False, в зависимости от наличия опции --test_api