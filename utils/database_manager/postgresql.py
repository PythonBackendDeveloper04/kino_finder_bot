from typing import Union
import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool
from data import config
class Database:
    def __init__(self):
        self.pool: Union[Pool, None] = None
    async def connection(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME
        )

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    async def users_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
        id SERIAL PRIMARY KEY,
        fullname VARCHAR(255) NULL,
        telegram_id BIGINT NOT NULL UNIQUE,
        language VARCHAR(255) NULL
        );
        """
        await self.execute(sql, execute=True)

    async def channels_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Channels (
        id SERIAL PRIMARY KEY,
        channel_name VARCHAR(255) NULL,
        channel_id BIGINT NOT NULL UNIQUE,
        channel_members_count INT NOT NULL
        );
        """
        await self.execute(sql, execute=True)

    async def movies_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS movies (
        post_id VARCHAR(255) NULL,
        code BIGINT NOT NULL UNIQUE
        );
        """
        await self.execute(sql, execute=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=1)
        ])
        return sql, tuple(parameters.values())

    async def add_user(self, fullname, telegram_id,language:str = "uz"):
        sql = "INSERT INTO Users (fullname, telegram_id,language) VALUES($1, $2, $3) returning *"
        return await self.execute(sql, fullname, telegram_id,language,fetchrow=True)

    async def add_channel(self, channel_name, channel_id,channel_members_count):
        sql = "INSERT INTO Channels (channel_name, channel_id,channel_members_count) VALUES($1, $2, $3) returning *"
        return await self.execute(sql, channel_name,int(channel_id),int(channel_members_count),fetchrow=True)

    async def delete_channel(self,channel_id):
        sql = """
        DELETE FROM Channels WHERE channel_id = $1
        """
        return await self.execute(sql,int(channel_id),fetchrow=True)

    async def select_all_users(self):
        sql = "SELECT * FROM Users"
        return await self.execute(sql, fetch=True)

    async def select_all_channels(self):
        sql = "SELECT * FROM Channels"
        return await self.execute(sql,fetch=True)

    async def select_user(self,telegram_id):
        sql = "SELECT * FROM Users WHERE telegram_id=$1"
        return await self.execute(sql, telegram_id, fetchrow=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM Users"
        return await self.execute(sql, fetchval=True)

    async def update_user_language(self, language, telegram_id):
        sql = "UPDATE Users SET language=$1 WHERE telegram_id=$2"
        return await self.execute(sql, language, telegram_id, execute=True)

    async def add_movie(self, post_id, code):
        sql = "INSERT INTO movies (post_id, code) VALUES($1, $2) returning *"
        return await self.execute(sql, post_id, int(code),fetchrow=True)

    async def delete_movie(self,code):
        sql = """
        DELETE FROM movies WHERE code = $1
        """
        return await self.execute(sql,int(code),fetchrow=True)

    async def select_all_movies(self):
        sql = "SELECT * FROM movies"
        return await self.execute(sql, fetch=True)

    async def select_movie(self,code):
        sql = "SELECT post_id FROM movies WHERE code=$1"
        return await self.execute(sql, int(code), fetchrow=True)