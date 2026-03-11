import sqlite3
# from Modules import task
from datetime import datetime

# conn = sqlite3.connect("Databases/test.db")
# conn.row_factory = sqlite3.Row

# cur = conn.cursor()
# cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
# tables = cur.fetchall()
# if "tasks" not in [table["name"] for table in tables]:
#     print("NOT")
# else: print("YES")
# cur.execute('''
#     CREATE TABLE IF NOT EXISTS tasks (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         title VARCHAR(50) NOT NULL,
#         description TEXT,
#         time VARCHAR(20) NOT NULL,
#         code TEXT NOT NULL,
#         trigger_time_list TEXT NOT NULL,
#         immediately BOOLEAN DEFAULT FALSE,
#         completed BOOLEAN DEFAULT FALSE,
#         trigger_count INTEGER DEFAULT 0,
#         target_count INTEGER DEFAULT 0,
#         is_send BOOLEAN DEFAULT FALSE,
#         send_url VARCHAR(255),
#         send_token VARCHAR(255)
#     )
# ''')

# conn.commit()
# data = task.Task(
#     id=0,
#     title="Test Task",
#     description="This is a test task.",
#     time=str(datetime.now()),
#     code="print('Hello, World!')",
#     trigger_time_list=[task.trigger_time(mouth=[1, 2, 3], week_day=[0, 1, 2], mouth_day=[1, 15], day_time=(12, 0))],
#     immediately=False,
#     completed=False,
#     trigger_count=0,
#     target_count=0,
#     is_send=False,
#     send_url="",
#     send_token=""
# )
# cur.execute('''
#     INSERT INTO tasks (title, description, time, code, trigger_time_list, immediately, completed, trigger_count, target_count, is_send, send_url, send_token)
#     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
# ''', data.to_tuple()
# )
# from Modules.task import Task
# from Modules.task import Trigger_time
# conn.commit()
# # conn.row_factory = sqlite3.Row
# cur.execute('SELECT * FROM tasks')
# tasks = cur.fetchall()
# for task in tasks:
#     print(type(task["trigger_time_list"]))
#     task = Task(**dict(task))
#     print(type(task.trigger_time_list))
#     print(type(task.trigger_time_list[0].mouth))
# conn.close()

# text = '''
# def test():

#     return "Hello, World!"
# '''
# namespace = {}
# exec(text, namespace)
# func = namespace["test"]
# print(func())
# import time
# print(datetime.now().second)


# from Modules.task import trigger_time

# t = trigger_time(
#     mouth=[1, 2, 3],
#     week_day=[0, 1, 2],
#     mouth_day=[1, 15],
#     day_time=(12, 0)
# )

# lst = [t, t, t]
# print(str(lst))
now = datetime.now()
print(now.day)