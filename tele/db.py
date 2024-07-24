import psycopg2 as psql
from django.core.checks import database
import os
from dotenv import load_dotenv
load_dotenv()


class Database:
    @staticmethod
    async def connect(query: str, query_type: str, select=None):
        db = psql.connect(
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
        )

        cursor = db.cursor()
        cursor.execute(query)
        data = ['insert', 'update', 'delete']
        if query_type in data:
            await db.commit()
        else:
            if select == 'one':
                return cursor.fetchone()
            else:
                return cursor.fetchall()


    @staticmethod
    async def check_user(phone_number: str):
        query = f"SELECT * FROM users_user WHERE phone_number = '{phone_number}'"
        user = await Database.connect(query, query_type='select', select="one")
        return user

    @staticmethod
    async def user_register(username: str, password: str, phone_number: str):
        query = f"INSERT INTO users_user(username, password, phone_number) VALUES('{username}', '{password}', '{phone_number}')"
        await Database.connect(query, query_type='insert')


    @staticmethod
    async def delivers():
        query = f"SELECT * FROM users_user"
        return await Database.connect(query, query_type='select')
