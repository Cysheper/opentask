from Modules.task import Task
import json
from Modules.Log import logging
import pathlib
import threading
import os

class TaskManager:
    # 1. 定义类变量 (类似于 C++ static)
    path = pathlib.Path("./Tasks/tasks_list.json")
    temp_file = path.with_suffix(".tmp")
    file_lock = threading.Lock()
    
    # 2. 类定义时立即执行：准备环境
    # 注意：这里的代码在整个程序生命周期只运行一次
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with file_lock:
            if not path.exists():
                with open(path, "w", encoding="utf-8") as f:
                    f.write("[]")
    except Exception as e:
        print(f"Critial Error during TaskManager initialization: {e}")

    @classmethod
    def load_tasks(cls) -> list:
        try:
            with cls.file_lock:
                with open(cls.path, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
            # 保持锁的粒度最小
            return [Task(**task) for task in raw_data]
        except Exception as e:
            logging.error(f"Failed to load tasks: {e}")
            return []
    
    @classmethod
    def save_tasks(cls, tasks: list) -> None:
        try:
            # 锁外处理数据
            tasks_dict = [task.to_dict() for task in tasks]
            data_to_write = json.dumps(tasks_dict, indent=4, ensure_ascii=False)
            
            with cls.file_lock:
                with open(cls.temp_file, "w", encoding="utf-8") as f:
                    f.write(data_to_write)
                # Windows 下 replace 是原子性的
                os.replace(cls.temp_file, cls.path)
                
        except Exception as e:
            logging.error(f"Failed to save tasks: {e}")
            # 直接通过类访问变量进行清理
            if cls.temp_file.exists():
                cls.temp_file.unlink()

    @classmethod
    def save_single_task(cls, task: Task) -> None:
        try:
            tasks = cls.load_tasks()
            # 更新或添加任务
            for i, existing_task in enumerate(tasks):
                if existing_task.id == task.id:
                    tasks[i] = task
                    break
            else:
                tasks.append(task)
            cls.save_tasks(tasks)
        except Exception as e:
            logging.error(f"Failed to save single task with id {task.id}: {e}")

    