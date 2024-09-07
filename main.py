import time
from InquirerPy import inquirer
from progress.bar import IncrementalBar
from src.catalog.catalog import create_catalog_instance

'''
name = inquirer.text(message="What's your name:").execute()
fav_lang = inquirer.select(
    message="What's your favourite programming language:",
    choices=["Go", "Python", "Rust", "JavaScript"],
).execute()
confirm = inquirer.confirm(message="Confirm?").execute()
'''


main_menu = []
sub_menu = []


def start_app():
    choice = inquirer.select(
        message="This app for testing https://detalum.ru/\n select start to continue or stop to exit:",
        choices=['start', 'exit'],
    ).execute()

    if choice == 'start':
        name = inquirer.text(message="Введите название каталога:").execute()
        catalog = create_catalog_instance(catalog_name=name.lower())
        response = catalog.get_tree()

        if response.status_code == 200:
            data = response.json().get('data')
            if data:
                bar = IncrementalBar(f'{catalog.name} get categories', max=len(data), suffix='%(index)d/%(max)d ')
                for category_data in data:
                    bar.next()
                    time.sleep(0.1)
                    catalog.add_category(data=category_data)
                bar.finish()
            else:
                catalog.logger.warning(f'No data in {catalog.name} {catalog.current_url}')
        else:
            catalog.logger.warning(f'Bad request {catalog.name} {catalog.current_url}')

        if catalog.categories:
            main_menu = [category.name for category in catalog.categories.values()]
            open_menu(menu=main_menu)

    elif choice == 'stop':
        exit()


def open_menu(menu):
    menu_list = menu + ['назад']
    choice = inquirer.select(
        message="select category:",
        choices=menu_list,
        height=len(menu_list),
    ).execute()

    if choice == 'назад':
        start_app()
    else:
        print(choice)



if __name__ == '__main__':
    start_app()