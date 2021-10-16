# file: create_chat.py
from enum import Enum, auto


class State(Enum):
    WAIT_TEACHER_ID = auto()
    WAIT_TEACHER_NAME = auto()
    CHOICE_PHONE_ID = auto()
    WAIT_STUDENT_ID = auto()
    WAIT_STUDENT_PHONE = auto()
    WAIT_STUDENT_NAME = auto()
    CHOICE_WELCOME = auto()
    WAIT_COMPLETE = auto()
    DELETE_CHAT = auto()
    ADD_ADMIN = auto()
    DELETE_ADMIN = auto()


class Chat:
    admin_id = None
    admin_state = None
    send_welcome_flag = True

    chat_id = -1

    teacher_id = -1
    teacher_nick = ''
    teacher_name = ''

    student_id = -1
    student_phone = ''
    student_nick = ''
    student_name = ''