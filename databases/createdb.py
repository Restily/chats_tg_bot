import sqlite3

def create_database():
    try:
        sqlite_connection = sqlite3.connect('chats.db')
        sqlite_create_table_query = '''CREATE TABLE chats (
                                    chat_id BIGINT,
                                    teacher_id BIGINT,
                                    teacher_nick VARCHAR(255),
                                    teacher_name VARCHAR(255),
                                    student_id BIGINT,
                                    student_phone VARCHAR(255),
                                    student_nick VARCHAR(255),
                                    student_name VARCHAR(255))'''
        cursor = sqlite_connection.cursor()
        print("База данных подключена к SQLite")

        cursor.execute(sqlite_create_table_query)
        sqlite_connection.commit()

        print("Таблица SQLite создана")

        cursor.close()

    except Exception as error:
        print(error)

create_database()