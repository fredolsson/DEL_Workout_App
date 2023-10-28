
import doctest
from help_methods import *


user_id = 13
chat_history_object = execute("SELECT * FROM generation_chat_history WHERE user_id = %s ORDER BY id;", [user_id], commit=False)
chat_history = []
for message in chat_history_object:
    msg_object = {"role": message[3], "content": message[2]}
    chat_history.append(msg_object)
print("saving goals")
chat_history.pop(0)
 # ta bort prompt
set_goals(chat_history, user_id) # skicka allt förutom prompt
print("information inserted")

