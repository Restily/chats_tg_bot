# file: database.py
import sqlite3

from config import DATABASE_URL
import utils
from create_chat import Chat


# SQL
def insert_chat_to_database(Chat: object) -> bool:
    connection = sqlite3.connect(DATABASE_URL)
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
                        insert into chats (chat_id, teacher_id, teacher_nick, teacher_name, student_id, student_phone, student_nick, student_name) 
                        values (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            Chat.chat_id,
                            Chat.teacher_id,
                            Chat.teacher_nick,
                            Chat.teacher_name,
                            Chat.student_id,
                            Chat.student_phone,
                            Chat.student_nick,
                            Chat.student_name
        ))
        connection.commit()

    except Exception as error:
        print(error)

    cursor.close()
    connection.close()


def get_chat_id(student_id: int) -> int:
    connection = sqlite3.connect(DATABASE_URL)
    cursor = connection.cursor()

    try:
        cursor.execute("""
                        select chat_id 
                        from chats
                        where student_id = {}
                        """.format(student_id))
        
        chat_id = cursor.fetchone()

        if chat_id != None:
            chat_id = chat_id[0]

    except Exception as error:
        print(error)
        
        return None

    cursor.close()
    connection.close()

    return chat_id


def get_student_id(chat_id: int) -> int:
    connection = sqlite3.connect(DATABASE_URL)
    cursor = connection.cursor()

    try:
        cursor.execute("""
                        select student_id 
                        from chats
                        where chat_id = {}
                        """.format(chat_id))

        student_id = cursor.fetchone()

        if student_id != None:
            student_id = student_id[0]

    except Exception as error:
        print(error)

        return None

    cursor.close()
    connection.close()

    return student_id

def delete_chat(chat_id):
    connection = sqlite3.connect(DATABASE_URL)
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
                        delete from chats
                        where chat_id = {}
                        """.format(chat_id))
        connection.commit()
    
    except Exception as error:
        print(error)

        return None

    cursor.close()
    connection.close()


def get_chats_info():
    connection = sqlite3.connect(DATABASE_URL)
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
                        select teacher_nick, teacher_name, student_nick, student_name
                        from chats
                        order by teacher_nick
                        """)
        
        chats = cursor.fetchall()
        
        chats_message = utils.chats_into_message(chats)

    except Exception as error:
        print(error)

        return None

    cursor.close()
    connection.close()

    return chats_message


def get_chats():
    connection = sqlite3.connect(DATABASE_URL)
    cursor = connection.cursor()
    
    all_chats = []

    try:
        cursor.execute("""
                        select chat_id, teacher_nick, teacher_name, student_nick, student_name
                        from chats
                        order by teacher_nick
                        """)
        
        chats = cursor.fetchall()
        
        for i in range(len(chats)):
            all_chats.append(chats[i][0])

        chats_message = utils.chats_into_message(chats, flag=1)

    except Exception as error:
        print(error)

        return None

    cursor.close()
    connection.close()

    return all_chats, chats_message

# pysondb
# def insert_chat_to_database(Chat: object) -> bool:
#     data = db.getDb('databases/data.json')
    
#     try:
#         data.add({
#             'chat_id':Chat.chat_id,
#             'teacher_id':Chat.teacher_id,
#             'teacher_nick':Chat.teacher_nick,
#             'teacher_name':Chat.teacher_name,
#             'student_id':Chat.student_id,
#             'student_nick':Chat.student_nick,
#             'student_name':Chat.student_name
#             })

#     except Exception as error:
#         print(error)


# def get_chat_id(student_id: int) -> int:
#     data = db.getDb('databases/data.json')

#     try:
#         chat = data.getBy({'student_id': student_id})

#         if not chat:
#             return None
        
#         return chat[0]['chat_id']

#     except Exception as error:
#         print(error)
        
#         return None


# def get_student_id(chat_id: int) -> int:
#     data = db.getDb('databases/data.json')

#     try:
#         chat = data.getBy({'chat_id': chat_id})

#         if not chat:
#             return None
        
#         return chat[0]['student_id']


#     except Exception as error:
#         print(error)

#         return None


# def get_chats_info() -> str:
#     """
#     Получение данных из бд в виде
#         1. Репетитор1 (Имя) - Ученик1 (Имя)
#         2. Репетитор1 (Имя) - Ученик2 (Имя)
#         ...
#     """
#     data = db.getDb('databases/data.json')

#     try: 
#         chats = data.getAll()
        
#         chats_message = utils.chats_into_message(chats)

#         return chats_message

#     except Exception as error:
#         print(error)

#         return None


# Test
# chat = Chat
# chat.teacher_id = 2
# chat.student_id = 3
# chat.teacher_name = 'Keklik'
# chat.teacher_nick = '@Keklik'
# chat.student_name = 'Lolik'
# chat.student_nick = '@Lolik'

