# file: utils.py

#SQL
def chats_into_message(pairs, flag=0) -> str:
    if pairs == []:
        return 'В базе данных нет записей'
        
    pairs_message = ['{}. {} ({}) - {} ({})'.format(
        i + 1,
        pairs[i][0+flag], # teacher_nick
        pairs[i][1+flag], # teacher_name
        pairs[i][2+flag], # student_nick
        pairs[i][3+flag]  # student_name
    ) for i in range(len(pairs))]

    return '\n'.join(pairs_message)

# pysondb
# def chats_into_message(chats: list[dict]) -> str:
#     if chats == []:
#         return 'В базе данных нет записей'
        
#     pairs_message = ['{}. {} ({}) - {} ({})'.format(
#         i + 1,
#         chats[i]['teacher_nick'], # teacher_nick
#         chats[i]['teacher_name'], # teacher_name
#         chats[i]['student_nick'], # student_nick
#         chats[i]['student_name']  # student_name
#     ) for i in range(len(chats))]

#     return '\n'.join(pairs_message)