from pymongo import MongoClient
import sqlite3
import json


if __name__ == "__main__":
    # Загрузка данных JSON
    f = open('quotes.json')
    quotes_json = json.load(f)
    f.close()

    # MONGO DB *****************************************************************************************************
    # Соединение с MongoDB
    client_mongo = MongoClient('mongodb://localhost:27017/')

    mv_lesson_4 = client_mongo["mv_lesson_4"]

    # Если коллекция существует, удаляем ее
    list_of_collections = mv_lesson_4.list_collection_names()
    if "quotes" in list_of_collections:
        mv_lesson_4["quotes"].drop()

    # Запись данных в БД
    collection_quotes = mv_lesson_4["quotes"]
    collection_quotes.insert_many(quotes_json)

    # Отобразим коллекции в БД
    print(f'Коллекции в БД: {mv_lesson_4.list_collection_names()}')

    # Чтение данных из БД
    print('\nЧтение данных из БД Mongo:')
    quotes_cursor = collection_quotes.find()
    quotes = list(quotes_cursor)
    n_quotes = len(quotes)
    print(f'Число статей в БД: {n_quotes}')

    for quote in quotes:
        print(quote)

    # SQLite ******************************************************************************************************
    # Создаем базу
    con = sqlite3.connect('quotes.db')

    cursor = con.cursor()

    sql_str = '''
        create table if not exists quotes(
            id integer primary key autoincrement,
            author text,
            tags text,
            q_text text
        )
    '''
    cursor.execute(sql_str)
    con.commit()

    # Очистка данных
    sql_str = 'delete from quotes'
    cursor.execute(sql_str)
    con.commit()

    # Запись данных в БД
    for quote in quotes_json:
        author = quote['author']
        tags = quote['tags']
        text = quote['text'].replace("'", "''").replace('"', "''")
        sql_str = f"insert into quotes(author, tags, q_text) values('{author}', '{tags}', '{text}')"
        # print(sql_str)
        cursor.execute(sql_str)
    con.commit()

    # Чтение данных из БД
    print('\nЧтение данных из БД SQLite:')
    cursor.execute("select count(id) from quotes")
    cnt = cursor.fetchone()
    print(f'Число записей в БД: {cnt[0]}')
    cursor.execute("select * from quotes")
    quotes = cursor.fetchall()
    for quote in quotes:
        print(quote)