import aiosqlite
import os


if os.path.exists('db.sqlite'):
    os.remove('db.sqlite')


async def initialize_db():
    async with aiosqlite.connect('db.sqlite', timeout=30) as db:
        await db.execute(
            '''
                CREATE TABLE IF NOT EXISTS catalogs (
                    catalog_name TEXT PRIMARY KEY
                )
            '''
        )

        await db.execute(
            '''
                CREATE TABLE IF NOT EXISTS categories (
                    category_id INTEGER,
                    name TEXT,
                    catalog_name TEXT,
                    PRIMARY KEY (category_id, catalog_name),
                    FOREIGN KEY (catalog_name) REFERENCES catalogs(catalog_name)
                )
            '''
        )

        await db.execute(
            '''
                CREATE TABLE IF NOT EXISTS parts_lists (
                    parts_list_id INTEGER PRIMARY KEY,
                    root_id INTEGER,
                    name TEXT,
                    catalog_name TEXT,
                    FOREIGN KEY (root_id, catalog_name) REFERENCES categories(category_id, catalog_name)
                )
            '''
        )

        await db.execute(
            '''
                CREATE TABLE IF NOT EXISTS details (
                    detail_id INTEGER PRIMARY KEY,
                    category_id INTEGER,
                    catalog_name TEXT,
                    name TEXT,
                    FOREIGN KEY (category_id, catalog_name) REFERENCES categories(category_id, catalog_name)
                )
            '''
        )

        await db.commit()


async def add_catalog(name: str):
    async with aiosqlite.connect('db.sqlite', timeout=30) as db:
        await db.execute(
            '''
                INSERT OR IGNORE INTO catalogs (catalog_name)
                VALUES(?)
            ''', (name,)
        )
        await db.commit()


async def add_category(category_id: int, name: str, catalog_name: str):
    async with aiosqlite.connect('db.sqlite', timeout=30) as db:
        await db.execute(
            '''
                INSERT OR IGNORE INTO categories (category_id, name, catalog_name)
                VALUES (?, ?, ?)
            ''', (category_id, name, catalog_name)
        )
        await db.commit()


async def add_parts_list(root_id: int, parts_list_id: int, name: str, catalog_name: str):
    async with aiosqlite.connect('db.sqlite', timeout=30) as db:
        async with db.execute(
                '''
                    SELECT * FROM categories WHERE category_id = ? AND catalog_name = ?
                ''', (root_id, catalog_name)
        ) as cursor:
            category = await cursor.fetchone()

        if category:
            await db.execute(
                '''
                    INSERT OR IGNORE INTO parts_lists (parts_list_id, name, root_id, catalog_name)
                    VALUES (?, ?, ?, ?)
                ''', (parts_list_id, name, root_id, catalog_name)
            )
            await db.commit()
        else:
            print(f"Database: Catalog with name {catalog_name} Category with ID {root_id} not found.")


async def count_parts_list(category_id: int, catalog_name: str):
    async with aiosqlite.connect('db.sqlite', timeout=30) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM parts_lists WHERE root_id = ? AND catalog_name = ?", (category_id, catalog_name)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0]
    return 0


async def add_detail(detail_id: int, name: str, category_id: int, catalog_name: str):
    async with aiosqlite.connect('db.sqlite', timeout=30) as db:
        await db.execute(
            '''
                INSERT OR IGNORE INTO details (detail_id, name, category_id, catalog_name)
                VALUES (?, ?, ?, ?)
            ''', (detail_id, name, category_id, catalog_name)
        )
        await db.commit()


async def count_parts(category_id: int, catalog_name: str):
    async with aiosqlite.connect('db.sqlite', timeout=30) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM details WHERE category_id = ? AND catalog_name = ?", (category_id, catalog_name)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0]
    return 0


async def fetch_all_parts_lists(category_id: int, catalog_name: str):
    async with aiosqlite.connect('db.sqlite', timeout=30) as db:
        async with db.execute(
                "SELECT parts_list_id, name, root_id FROM parts_lists WHERE root_id = ? AND catalog_name = ?",
                (category_id, catalog_name)
        ) as cursor:
            parts_lists = await cursor.fetchall()
            return parts_lists


async def fetch_parts_lists_batch(category_id, catalog_name, batch_size, offset):
    async with aiosqlite.connect('db.sqlite', timeout=30) as db:
        async with db.execute(
            "SELECT parts_list_id, name, root_id FROM parts_lists WHERE root_id = ? AND catalog_name = ? LIMIT ? OFFSET ?",
            (category_id, catalog_name, batch_size, offset)
        ) as cursor:
            return await cursor.fetchall()


async def fetch_parts(category_id: int, catalog_name: str):
    async with aiosqlite.connect('db.sqlite', timeout=30) as db:
        async with db.execute(
                "SELECT detail_id, name, category_id FROM details WHERE category_id = ? AND catalog_name = ?",
                (category_id, catalog_name)
        ) as cursor:
            parts = await cursor.fetchall()
            return parts


async def fetch_parts_batch(category_id, catalog_name, batch_size, offset):
    async with aiosqlite.connect('db.sqlite', timeout=30) as db:
        async with db.execute(
                "SELECT detail_id, name, category_id FROM details WHERE category_id = ? AND catalog_name = ? LIMIT ? OFFSET ?",
                (category_id, catalog_name, batch_size, offset)
        ) as cursor:
            return await cursor.fetchall()
