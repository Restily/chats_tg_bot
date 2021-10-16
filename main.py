# file: main.py
import os

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl import types
from telethon.tl.types import PeerChannel, PeerUser, Message
from telethon.tl.functions.channels import CreateChannelRequest, InviteToChannelRequest, DeleteChannelRequest
from telethon.tl.functions.users import GetFullUserRequest

from databases import database
from config import API_HASH, API_ID, SESSION_STRING, ADMIN_ID, CLIENT_ID
from create_chat import State, Chat

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)


admins = [ADMIN_ID]
admins_nicknames = ['@aidreika']
del_chats = []


async def send_welcome_messages(Chat: object) -> bool:
    """
    Отправка приветственных сообщений репетитору и ученику
    """
    try:
        # Отправка сообщения ученику
        await client.send_message(Chat.student_id, 'Здравствуй, {}, я твой репетитор. Меня зовут {}'.format(
            Chat.student_name,
            Chat.teacher_name
        ))

        #Отправка сообщения репетитору
        await client.send_message(Chat.chat_id, 'Здравствуйте, {}, я Ваш ученик. Меня зовут {}'.format(
            Chat.teacher_name,
            Chat.student_name
        ))

        return True

    except Exception as error:
        print(error)

        return False


async def create_chat(Chat: object) -> bool:
    """ 
    Создание чата
    
    Args:
        :admins (`list`): список админов
        :user (`str`): никнейм пользователя (преподавателя)
        :title (`str`): название беседы (имя ученика)
    
    Return:
        True при успешном создании беседы, иначе False
    """
    try:
        # Создаём беседу
        chat = await client(CreateChannelRequest(
            title = Chat.student_name,
            about = 'Chat',
            megagroup = True
        ))

        chat_id = chat.updates[1].channel_id
        Chat.chat_id = chat_id

        admins = [ADMIN_ID]
        if Chat.admin_id != None:
            admins.append(Chat.admin_id)

        # Приглашаем админа в беседу
        await client(InviteToChannelRequest(
            channel=chat_id,
            users=admins
        ))

        # Даём права анонимного администратора боту и админу
        await client.edit_admin(chat_id, user=CLIENT_ID, anonymous=True)
        for admin in admins:
            await client.edit_admin(chat_id, user=admin, is_admin=True, anonymous=True)

        # Добавляем в беседу преподавателя
        await client(InviteToChannelRequest(
            channel=chat_id,
            users=[Chat.teacher_id]
        ))

        # Отправляем приветственные сообщения 
        if Chat.send_welcome_flag:
            await send_welcome_messages(Chat)

        # Добавляем в базу данных запись о чате
        database.insert_chat_to_database(Chat)
        
        return True

    except Exception as error:
        print(error)

        return False


async def file_processing(message: types.Message, object_entity):
    try:
        # скачиваем файл
        file_path = await client.download_media(message.media, file='files') 
        print(file_path)

        await client.send_file(entity=object_entity, silent=True, file=file_path) # отправляем файл

        os.remove(file_path) # удаляем файл

    except Exception as error:
        print(error)


@client.on(events.NewMessage(chats=(ADMIN_ID)))
async def admin_commands(message: types.Message):
    """
    Админка

    Commands:
        /AddChat - создать новую комнату
        /ShowChats - посмотреть таблицу с чатами
        /DeleteChat - удалить чат
        /AddAdmin - добавить нового администратора
        /ShowAdmins - получить список администраторов
        /DeleteAdmin - удалить администратора
        /Restart - инициализация бота
    """
    admin_nick = (await message.get_sender()).username
    admin = await client.get_entity(PeerUser(admin_nick))

    state = Chat.admin_state

    if state == None:
        if message.text == '/Restart':
            await client.get_dialogs()

            await client.send_message(admin, 'Бот успешно проинициализирован')
        
        elif message.text == '/Commands':
            await client.send_message(admin, "/AddChat - создать новую комнату\n/ShowChats - посмотреть таблицу с чатами\n/DeleteChat - удалить чат\n/AddAdmin - добавить нового администратора\n/ShowAdmins - получить список администраторов\n/DeleteAdmin - удалить администратора")

        elif message.text == '/AddChat':
            return message.text

        elif message.text == '/ShowChats':
            pairs = database.get_chats_info()

            await client.send_message(admin, pairs)

        elif message.text == '/DeleteChat':
            all_chats, chats_message = database.get_chats()

            if all_chats == []:
                await client.send_message(admin, "Чатов не существует")

            global del_chats
            del_chats = all_chats

            Chat.admin_state = State.DELETE_CHAT

            await client.send_message(admin, chats_message)

            await client.send_message(admin, "Введите номер беседы, которую необходимо удалить")

        elif message.text == '/AddAdmin':
            Chat.admin_state = State.ADD_ADMIN

            await client.send_message(admin, 'Ввведите @id преподавателя для добавления в администраторы')
        
        elif message.text == '/DeleteAdmin':
            if len(admins) > 1:
                await client.send_message(admin, "Введите номер администратора:\n" + 
                                            '\n'.join([str(i) + '. ' + admins[i] for i in range(1, len(admins))]))
            else:
                await client.send_message(admin, 'Вы ещё не добавили администраторов')

            Chat.admin_state = State.DELETE_ADMIN

        elif message.text == '/ShowAdmins':
            if len(admins) > 1:
                await client.send_message(admin, "Администраторы:\n" + '\n'.join(admins_nicknames[1:]))
            else:
                await client.send_message(admin, 'Вы ещё не добавили администраторов')

        else:
            await client.send_message(admin, "Чтобы посмотреть список комманд, введите /Commands")

    elif state == State.DELETE_CHAT:
        chats_num = message.text

        try:            
            chat_id = int(del_chats[int(chats_num) - 1])

            await client(DeleteChannelRequest(
                channel=PeerChannel(chat_id)
            ))

            database.delete_chat(chat_id)

            await client.send_message(admin, 'Беседа успешно удалена')

        except Exception as error:
            print(error)

            await client.send_message(admin, 'Произошла ошибка. Введите команду /Deletechat и попробуйте ещё раз')
        
        Chat.admin_state = None

    elif state == State.DELETE_ADMIN:
        admin_ind = message.text

        try:        
            admins.pop(int(admin_ind) - 1)
            admins_nicknames.pop(int(admin_ind) - 1)

            await client.send_message(admin, 'Администратор успешно удалён')
        except:
            await client.send_message(admin, 'Попробуйте ещё раз')
        
        Chat.admin_state = None

    elif state == State.ADD_ADMIN:
        admin_nick = message.text

        try:
            new_admin = await client(GetFullUserRequest(admin_nick))

            admins_nicknames.append(admin_nick)
            admins.append(new_admin.user.id)

            await client.send_message(admin, 'Администратор успешно добавлен')

            Chat.admin_state = None

        except Exception as error:
            await client.send_message(admin, 'Вы ввели недействительный @id. Проверьте id и введите его ещё раз')


@client.on(events.NewMessage())
async def create_chat_command(message: types.Message):
    """
    Функция для создания нового чата
    
    Args:
        :message (`message`): сообщение (от администратора бота)
    """
    try:
       if message.peer_id.user_id not in admins:
           return True
    except:
        return True

    cur_admin_nick = (await message.get_sender()).username
    cur_admin = await client.get_entity(PeerUser(cur_admin_nick))
    state = Chat.admin_state

    if state == None:
        if message.text == '/AddChat':
            await client.send_message(cur_admin, 'Введите @id преподавателя')
            Chat.admin_state = State.WAIT_TEACHER_ID
        
        else:
            if cur_admin.id != ADMIN_ID:
                await client.send_message(cur_admin, 'Чтобы создать комнату, введите /AddChat')

    elif state == State.WAIT_TEACHER_ID:
        teacher_id = message.text

        try:
            teacher = await client(GetFullUserRequest(teacher_id))
            Chat.teacher_nick = message.text
            Chat.teacher_id = teacher.user.id

            await client.send_message(cur_admin, 'Введите имя преподавателя')
            Chat.admin_state = State.WAIT_TEACHER_NAME

        except Exception as error:
            await client.send_message(cur_admin, 'Вы ввели недействительный @id. Проверьте id и попробуйте ещё раз')

    elif state == State.WAIT_TEACHER_NAME:
        Chat.teacher_name = message.text

        await client.send_message(cur_admin, 'Введите 1, чтобы зарегестрировать ученика по номеру, либо 2, чтобы зарегестрировать по никнейму (@id)')

        Chat.admin_state = State.CHOICE_PHONE_ID

    elif state == State.CHOICE_PHONE_ID:
        # Регистрация по номеру
        if message.text == '1':
            await client.send_message(cur_admin, 'Введите номер телефона ученика')

            Chat.admin_state = State.WAIT_STUDENT_PHONE

        # Регистрация по id (никнейму)
        elif message.text == '2':
            await client.send_message(cur_admin, 'Введите @id ученика')

            Chat.admin_state = State.WAIT_STUDENT_ID

        else:
            await client.send_message(cur_admin, 'Введите 1, чтобы зарегестрировать ученика по номеру, либо 2, чтобы зарегестрировать по никнейму')

    elif state == State.WAIT_STUDENT_PHONE:
        if message.text == '2':
            await client.send_message(cur_admin, 'Введите @id ученика')

            Chat.admin_state = State.WAIT_STUDENT_ID

            return True

        student_phone = message.text

        try:
            student = await client.get_entity(student_phone)
            Chat.student_phone = student_phone
            Chat.student_nick = f'@{student.username}'
            Chat.student_id = student.id

            await client.send_message(cur_admin, 'Введите имя ученика')
            Chat.admin_state = State.WAIT_STUDENT_NAME

        except Exception as error:
            print(error)
            
            await client.send_message(cur_admin, 'Вы ввели недействительный номер телефона, либо телефон скрыт настройками приватности. Введите 2, чтобы зарегестрировать по id, или проверьте номер и попробуйте ещё раз')

    elif state == State.WAIT_STUDENT_ID:
        student_nick = message.text

        try:
            student = await client(GetFullUserRequest(student_nick))

            Chat.student_nick = student_nick 
            Chat.student_id = student.user.id

            await client.send_message(cur_admin, 'Введите имя ученика')
            Chat.admin_state = State.WAIT_STUDENT_NAME

        except Exception as error:
            await client.send_message(cur_admin, 'Вы ввели недействительный @id. Проверьте id и попробуйте ещё раз')

    elif state == State.WAIT_STUDENT_NAME:
        Chat.student_name = message.text

        await client.send_message(cur_admin, 'Введите "да" или "нет", чтобы отправить приветственное сообщение')
        Chat.admin_state = State.CHOICE_WELCOME
        
    elif state == State.CHOICE_WELCOME:
        if message.text.lower() == 'да':
            Chat.send_welcome_flag = True

        elif message.text.lower() == 'нет':
            Chat.send_welcome_flag = False

        else:
            await client.send_message(cur_admin, 'Введите "да" или "нет", чтобы отправить приветственное сообщение')

            return True

        await client.send_message(cur_admin, 'Проверьте данные:\nId преподавателя: {}\nИмя преподавателя: {}\nId ученика: {}\nИмя ученика: {}\n\nВведите "да", если данные правильные, иначе введите "нет"'.format(
            Chat.teacher_nick,
            Chat.teacher_name,
            Chat.student_nick,
            Chat.student_name
        ))
    
        Chat.admin_state = State.WAIT_COMPLETE
    
    elif state == State.WAIT_COMPLETE:
        msg = message.text.lower()

        if msg == 'да':
            if message.peer_id.user_id != ADMIN_ID:
                Chat.admin_id = message.peer_id.user_id

            chat_flag = await create_chat(Chat)

            if chat_flag:
                await client.send_message(cur_admin, 'Беседа успешно создана')

                if message.peer_id.user_id != ADMIN_ID:
                    await client.send_message(ADMIN_ID, 'Администратор {} создал беседу:\n Id преподавателя: {}\nИмя преподавателя: {}\nId ученика: {}\nИмя ученика: {}'.format(
                        cur_admin_nick,
                        Chat.teacher_nick,
                        Chat.teacher_name,
                        Chat.student_nick,
                        Chat.student_name
                    ))
            else:
                await client.send_message(cur_admin, 'Не получилось создать беседу. Попробуйте создать беседу позднее')
            
            Chat.admin_id = None
            Chat.admin_state = None

        elif msg == 'нет':
            await client.send_message(cur_admin, 'Беседа не была создана. Введите /CreateChat, чтобы создать беседу')
        
            Chat.admin_state = None

        else:
            await client.send_message(cur_admin, 'Введите "да", если данные правильные, иначе введите "нет"')


@client.on(events.NewMessage())
async def get_new_messages(message: types.Message):
    """
    Обработчтик новых сообщений
    """
    peer_id = message.peer_id

    # Проверка, написал ли нам пользователь 
    # или сообщение пришло из канала
    # try:
    if isinstance(peer_id, PeerUser):   
        user_id = peer_id.user_id

        if user_id == ADMIN_ID:
            return True

        chat_id = database.get_chat_id(user_id) # получаем id чата

        if chat_id != None:
            chat = await client.get_entity(PeerChannel(chat_id))

            if chat_id != None and message.text != '': # отправляем сообщение
                await client.send_message(entity=chat, message=message.text)

            if message.media != None: # отправляем файлы
                await file_processing(message, chat)

    elif isinstance(peer_id, PeerChannel):
        channel_id = peer_id.channel_id

        student_id = database.get_student_id(channel_id) # получаем id ученика
        
        if student_id != None:
            student = await client.get_entity(PeerUser(student_id))

            if message.text != '': # отправляем сообщение
                await client.send_message(entity=student, message=message.text)
            
            if message.media != None: # отправляем файлы
                await file_processing(message, student)

    # except Exception as error:
    #     print(error)

    #     return True


if __name__ == '__main__':
    client.start()
    client.run_until_disconnected()