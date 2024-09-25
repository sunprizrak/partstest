import threading
import time
import pytest
import requests
from InquirerPy import inquirer
from colorama import Fore, init
from tqdm import tqdm
from itertools import cycle

# Инициализация colorama
init(autoreset=True)


def update_spinner(spin, spin_text, spin_event):
    spinner_cycle = cycle(['-', '\\', '|', '/'])
    while not spin_event.is_set():
        spin.set_description(f"{spin_text} {next(spinner_cycle)}")
        spin.refresh()
        time.sleep(0.1)


class Level:

    def __init__(self):
        self.count = 0
        self.menu = {}

    def __add__(self, other):
        self.count += other

    def __sub__(self, other):
        if self.count > 0:
            self.count -= other

    def __gt__(self, other):
        return self.count > other

    def add_menu(self, value):
        self.menu[self.count] = value

    def get_menu(self):
        return self.menu[self.count]

    def clean(self):
        self.count = 0
        self.menu.clear()


level = Level()


def start_app():
    print(Fore.GREEN + 'App for testing API https://detalum.ru/')
    choice = inquirer.select(
        message="Choice continue or exit:",
        qmark='',
        amark='',
        choices=['continue', 'exit'],
    ).execute()

    if choice == 'continue':
        spinner_text = Fore.CYAN + 'Loading Brands'
        spinner = tqdm(total=0, bar_format="{desc}", ncols=30)
        stop_spinner = threading.Event()

        thread = threading.Thread(target=update_spinner, args=(spinner, spinner_text, stop_spinner))
        thread.start()

        url = 'http://api.catalog.detalum.ru/api/v1/brand'
        response = requests.get(url)

        brands = dict()

        if response.status_code == 200:
            data = response.json().get('data')
            if data:
                brands = {brand.get('label'): brand.get('slug') for brand in data}
            else:
                print(Fore.RED + f'No data in responuse {url}')
        else:
            print(Fore.RED + f'Bad request {url}')

        stop_spinner.set()
        spinner.set_description(Fore.CYAN + 'Brands loaded')
        spinner.close()
        thread.join()

        if brands:
            level + 1
            brands['Тест API для всех каталогов'] = f"-s -v tests/test_catalog.py::TestCatalog::test_root_categories tests/test_catalog.py::TestCatalog::test_tree tests/test_catalog.py::TestCatalog::test_parts --catalogs={','.join(brands.values())} --test_api --alluredir allure_results"
            level.add_menu(brands)
            open_menu()
        else:
            print(Fore.YELLOW + '\n No Brands.')
            start_app()

    elif choice == 'exit':
        exit()


def open_menu(**kwargs):
    menu = level.get_menu()

    if isinstance(menu, tuple):
        menu = menu[0]

    menu_list = [elem for elem in menu] + ['<<< назад >>>']
    message = "\nSelect Brand:"

    if kwargs.get('brand'):
        brand = kwargs.get('brand')
        message = f"Brand {brand}:"

    choice = inquirer.select(
        message=message,
        choices=menu_list,
        qmark='',
        amark='',
        height=len(menu_list),
    ).execute()

    if choice.lower()[:4] == 'тест':
        command = menu.get(choice).split()
        pytest.main(command)
        open_menu()
    elif choice == '<<< назад >>>':
        level - 1
        if level > 0:
            open_menu()
        else:
            level.clean()
            start_app()
    else:
        brand_slug = menu.get(choice)
        catalog_menu = {
                'Тест каталога': f'-s -v tests/test_catalog.py::TestCatalog::test_root_categories tests/test_catalog.py::TestCatalog::test_tree tests/test_catalog.py::TestCatalog::test_parts --catalogs={brand_slug} --alluredir allure_results',
                'Тест дерева': f'-s -v tests/test_catalog.py::TestCatalog::test_root_categories tests/test_catalog.py::TestCatalog::test_tree --catalogs={brand_slug} --alluredir allure_results',
                'Тест корневых категорий': f'-s -v tests/test_catalog.py::TestCatalog::test_root_categories --catalogs={brand_slug} --alluredir allure_results',
                'Тест API': f'-s -v tests/test_catalog.py::TestCatalog::test_root_categories tests/test_catalog.py::TestCatalog::test_tree tests/test_catalog.py::TestCatalog::test_parts --catalogs={brand_slug} --test_api --alluredir allure_results',
        },
        level + 1
        level.add_menu(catalog_menu)
        open_menu(brand=choice)


if __name__ == '__main__':
    start_app()


