import asyncio
from asyncio import timeout

import aiosqlite
import os


if os.path.exists('db.sqlite'):
    os.remove('db.sqlite')


async def initialize_db():
    async with aiosqlite.connect('db.sqlite', timeout=30) as db:
        await db.execute(
            '''
                CREATE TABLE IF NOT EXISTS categories (
                    category_id INTEGER PRIMARY KEY,
                    name TEXT
                )
            '''
        )

        await db.execute(
            '''
                CREATE TABLE IF NOT EXISTS parts_lists (
                    parts_list_id INTEGER PRIMARY KEY,
                    root_id INTEGER,
                    name TEXT,
                    FOREIGN KEY (root_id) REFERENCES categories(category_id)
                )
            '''
        )

        await db.execute(
            '''
                CREATE TABLE IF NOT EXISTS details (
                    detail_id INTEGER PRIMARY KEY,
                    category_id INTEGER,
                    name TEXT,
                    FOREIGN KEY (category_id) REFERENCES categories(category_id)
                )
            '''
        )

        await db.commit()


async def add_category(category_id: int, name: str):
    async with aiosqlite.connect('db.sqlite', timeout=30) as db:
        await db.execute(
            '''
                INSERT OR IGNORE INTO categories (category_id, name)
                VALUES (?, ?)
            ''', (category_id, name)
        )
        await db.commit()


async def add_parts_list(root_id: int, parts_list_id: int, name: str):
    async with aiosqlite.connect('db.sqlite', timeout=30) as db:
        async with db.execute(
                '''
                    SELECT * FROM categories WHERE category_id = ?
                ''', (root_id,)
        ) as cursor:
            category = await cursor.fetchone()

        if category:
            await db.execute(
                '''
                    INSERT OR IGNORE INTO parts_lists (parts_list_id, name, root_id)
                    VALUES (?, ?, ?)
                ''', (parts_list_id, name, root_id)
            )
            await db.commit()
        else:
            print(f"Database: Category with ID {root_id} not found.")


async def count_parts_list(category_id):
    async with aiosqlite.connect('db.sqlite', timeout=30) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM parts_lists WHERE root_id = ?", (category_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0]
    return 0


async def add_detail(detail_id: int, name: str, category_id: int):
    async with aiosqlite.connect('db.sqlite', timeout=30) as db:
        await db.execute(
            '''
                INSERT OR IGNORE INTO details (detail_id, name, category_id)
                VALUES (?, ?, ?)
            ''', (detail_id, name, category_id)
        )
        await db.commit()


async def count_parts(category_id):
    async with aiosqlite.connect('db.sqlite', timeout=30) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM details WHERE category_id = ?", (category_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0]
    return 0


async def fetch_all_parts_lists(category_id):
    async with aiosqlite.connect('db.sqlite', timeout=30) as db:
        async with db.execute("SELECT parts_list_id, name, root_id FROM parts_lists WHERE root_id = ?",
                              (category_id,)) as cursor:
            parts_lists = await cursor.fetchall()
            return parts_lists


async def fetch_parts_lists_batch(category_id, batch_size, offset):
    async with aiosqlite.connect('db.sqlite', timeout=30) as db:
        async with db.execute(
            "SELECT parts_list_id, name, root_id FROM parts_lists WHERE root_id = ? LIMIT ? OFFSET ?",
            (category_id, batch_size, offset)
        ) as cursor:
            return await cursor.fetchall()


async def fetch_parts(category_id):
    async with aiosqlite.connect('db.sqlite', timeout=30) as db:
        async with db.execute("SELECT detail_id, name, category_id FROM details WHERE category_id = ?", (category_id,)) as cursor:
            parts = await cursor.fetchall()
            return parts


async def fetch_parts_batch(category_id, batch_size, offset):
    async with aiosqlite.connect('db.sqlite', timeout=30) as db:
        async with db.execute(
                "SELECT detail_id, name, category_id FROM details WHERE category_id = ? LIMIT ? OFFSET ?",
                (category_id, batch_size, offset)
        ) as cursor:
            return await cursor.fetchall()
