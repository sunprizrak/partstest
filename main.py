import asyncio
import aiohttp
import pytest
from InquirerPy import inquirer
from colorama import Fore, init
from tqdm import tqdm
from utility import update_spinner, get_ip_address
from database import initialize_db, clear_db

# Инициализация colorama
init(autoreset=True)


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


async def fetch_brands(session):
    url = 'http://api.catalog.detalum.ru/api/v1/brand'

    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            return {brand.get('label'): brand.get('slug') for brand in data.get('data', [])}
        else:
            print(Fore.RED + f'Bad request {url}')
            return None


async def start_app():
    try:
        print(Fore.GREEN + 'App for testing API https://detalum.ru/')

        choice = await inquirer.select(
            message="Choice continue or exit:",
            qmark='',
            amark='',
            choices=['continue', 'exit'],
        ).execute_async()

        if choice == 'continue':
            spinner = tqdm(total=0, bar_format="{desc}", ncols=30)
            spinner_text = Fore.CYAN + 'Loading Brands'
            spinner_event = asyncio.Event()
            spinner_task = asyncio.create_task(update_spinner(spin=spinner, spin_text=spinner_text, spin_event=spinner_event))
            try:
                async with aiohttp.ClientSession() as session:
                    brands = await fetch_brands(session)
            finally:
                spinner_event.set()
                await spinner_task
                spinner.set_description('Brands loaded')
                spinner.close()

            if brands:
                level + 1
                brands['Тест API для всех каталогов'] = f"-s -v tests/test_catalog.py::TestCatalog::test_root_categories tests/test_catalog.py::TestCatalog::test_tree tests/test_catalog.py::TestCatalog::test_parts --catalogs={','.join(brands.values())} --test_api --alluredir allure_results"
                ip_address = await get_ip_address()
                brands['Запустить Allure'] = f"allure serve --host {ip_address} --port 8080 allure_results"
                level.add_menu(brands)
                await open_menu()
            else:
                print(Fore.YELLOW + '\n No Brands.')
                await start_app()
        elif choice == 'exit':
            exit()
    except KeyboardInterrupt:
        exit()


async def open_menu(**kwargs):
    menu = level.get_menu()

    if isinstance(menu, tuple):
        menu = menu[0]

    menu_list = [elem for elem in menu] + ['<<< назад >>>']
    message = "\nSelect Brand:"

    if kwargs.get('brand'):
        brand = kwargs.get('brand')
        message = f"Brand {brand}:"

    choice = await inquirer.select(
        message=message,
        choices=menu_list,
        qmark='',
        amark='',
        height=len(menu_list),
    ).execute_async()

    if choice.lower()[:4] == 'тест':
        try:
            await clear_db()
            command = menu.get(choice).split()
            pytest.main(command)
        except SystemExit as error:
            print(f"Pytest завершён с кодом: {error.code}")
        finally:
            await open_menu()
    elif choice == 'Запустить Allure':
        command = menu.get(choice)
        try:
            process = await asyncio.create_subprocess_shell(command)
            await process.wait()
        except asyncio.CancelledError:
            print("Allure был завершён. Возврат в меню.")
            await open_menu()
        except KeyboardInterrupt:
            print("Процесс был прерван. Возврат в меню.")
        except Exception as e:
            print(f"Произошла ошибка при запуске Allure: {e}")
        finally:
            await open_menu()
    elif choice == '<<< назад >>>':
        level - 1
        if level > 0:
            await open_menu()
        else:
            level.clean()
            await start_app()
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
        await open_menu(brand=choice)


async def main():
    await initialize_db()
    await start_app()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except asyncio.CancelledError:
        exit()
    except KeyboardInterrupt:
        exit()
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        exit()



