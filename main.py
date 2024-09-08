import threading
import time
import pytest
import requests
from InquirerPy import inquirer
from progress.spinner import Spinner
from colorama import Fore, init

# Инициализация colorama
init(autoreset=True)

'''
name = inquirer.text(message="What's your name:").execute()
fav_lang = inquirer.select(
    message="What's your favourite programming language:",
    choices=["Go", "Python", "Rust", "JavaScript"],
).execute()
confirm = inquirer.confirm(message="Confirm?").execute()
'''


def update_spinner(spin, spin_event):
    while not spin_event.is_set():
        spin.next()
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
        spinner = Spinner(Fore.CYAN + 'Loading Brands ')
        stop_spinner = threading.Event()

        thread = threading.Thread(target=update_spinner, args=(spinner, stop_spinner))
        thread.start()

        url = 'http://api.catalog.detalum.ru/api/v1/brand'
        response = requests.get(url)

        brands = dict()

        if response.status_code == 200:
            data = response.json().get('data')
            if data:
                brands = {brand.get('label'): brand.get('slug') for brand in data}
                print(brands)
            else:
                print(Fore.RED + f'No data in responuse {url}')
        else:
            print(Fore.RED + f'Bad request {url}')

        stop_spinner.set()
        thread.join()

        if brands:
            level + 1
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
    brand_slug = None

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
                'Тест каталога': 1,
                'Тест дерева': 2,
                'Тест корневых категорий': f'-s -v tests/test_catalog.py::TestCatalog::test_root_categories --catalogs={brand_slug}',
                'Тест API': 4,
        },
        level + 1
        level.add_menu(catalog_menu)
        open_menu(brand=choice)





if __name__ == '__main__':
    start_app()


