from queue import Queue
from threading import Thread
import pathlib
from datetime import datetime
from Modules.task import Task, Trigger_time
import time
from Worker.worker_core import Worker
from Modules.Log import logging
import json


"""
The Scheduler class is responsible for managing and executing tasks based on 
their defined trigger times.
"""
class Scheduler:
    """
    Initializes the Scheduler instance by setting up the task queue,
    creating a Worker instance, and ensuring the existence of the tasks_list.json file. 
    It also starts two background threads: one for fetching tasks from the database and 
    another for executing tasks from the queue.
    """
    def __init__(self):
        self.task_queue = Queue()
        self.worker = Worker()
        self.path = pathlib.Path("./Tasks/tasks_list.json")
        if not self.path.exists():
            logging.info("tasks_list.json not found, creating tasks table in database.")
            with open(self.path, "w") as f:
                f.write("[]")
        else:   
            logging.info("Getted tasks from tasks_list.json.")
        Thread(target=self.get_tasks, daemon=True).start()
        Thread(target=self.execute_tasks, daemon=True).start()

    """
    Continuously fetches tasks from the database and checks if they 
    are due for execution based on their trigger times.
    """
    def get_tasks(self) -> None:

        while True:
            tasks: list[Task] = self.load_tasks()

            for task in tasks:
                if task.completed == True:
                    continue
                if task.immediately == True:
                    task.immediately = False
                    self.save_tasks(tasks)
                    self.task_queue.put(task)
                    continue

                trigger_time_list: list[Trigger_time] = []
                for trigger in task.trigger_time_list:
                    if isinstance(trigger, Trigger_time):
                        trigger_time_list.append(trigger)
                    elif isinstance(trigger, dict):
                        trigger_time_list.append(Trigger_time(**trigger))
                    else:
                        logging.error(f"Invalid trigger type for task {task.title}: {type(trigger)}")
                        continue
                
                for trigger in trigger_time_list:
                    if self.check_trigger_time(trigger):
                        self.task_queue.put(task)
                        break  # 同一任务同一轮只入队一次
            time.sleep(60)  # 每分钟检查一次任务是否到达触发时间

    """
    Checks if the current time matches the specified trigger time.
    """
    def check_trigger_time(self, trigger: Trigger_time) -> bool:

        now = datetime.now()
        if trigger.mouth and now.month not in trigger.mouth:
            return False
        if trigger.week_day and (now.weekday() + 1) not in trigger.week_day:
            return False
        if trigger.mouth_day and now.day not in trigger.mouth_day:
            return False
        if trigger.hour and trigger.minute is not None:
            if now.hour != trigger.hour or now.minute != trigger.minute:
                return False
        return True
    
    """
    Continuously executes tasks from the task queue using a Worker instance.
    After executing a task, it updates the trigger count in the database and 
    checks if the task has reached its target count to mark it as completed. 
    It also handles tasks that are set to execute immediately and have no trigger 
    times, marking them as completed after execution.
    """
    def execute_tasks(self) -> None:
        while True:
            task: Task = self.task_queue.get()
            self.worker.run(task)
            self.task_queue.task_done() # Mark the task as done in the queue    
            try:
                tasks: list[Task] = self.load_tasks()
                
                for t in tasks:
                    if t.id == task.id:
                        t.trigger_count += 1
                        logging.info(f"Task executed and updated: {task.title}, trigger count: {task.trigger_count + 1}")
                        if task.target_count > 0 and task.trigger_count + 1 >= task.target_count:
                            t.completed = True
                            logging.info(f"Task completed: {task.title}")   
                        break
                self.save_tasks(tasks)

            except Exception as e:
                logging.error(f"Failed to update task: {task.title} with error: {e}")

    """
    Loads tasks from the tasks_list.json file and returns them as a list of Task objects.
    Returns:
        list[Task]: A list of Task objects loaded from the database.
    """
    def load_tasks(self) -> list[Task]:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                tasks = list(json.load(f))
            # logging.info(f"Loaded {len(tasks)} tasks successfully.")
            return [Task(**dict(task)) for task in tasks]
        except Exception as e:
            logging.error(f"Failed to load tasks with error: {e}")
            return []
        

    """
    Saves a list of Task objects to the tasks_list.json file.
    
    Args:
        tasks (list[Task]): The list of Task objects to be saved.
    """
    def save_tasks(self, tasks: list[Task]) -> None:
        try:
            tasks_dict = [task.to_dict() for task in tasks]
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(tasks_dict, f, indent=4)
            # logging.info("Tasks saved successfully.")
        except Exception as e:
            logging.error(f"Failed to save tasks with error: {e}")


    """
    Adds a new task to the tasks_list.json file and assigns it a unique ID.
    """
    def add_task(self, task: Task) -> None:
       
        logging.info(f"Adding task: {task.title}")
        try:
            tasks: list[Task] = self.load_tasks()
            task.id = max([t.id for t in tasks], default=0) + 1
            tasks.append(task)
            self.save_tasks(tasks)
            logging.info(f"Task added: {task.title}")
        except Exception as e:
            logging.error(f"Failed to add task: {task.title} with error: {e}")
            raise e

    """
    Checks the health of the scheduler by verifying the connection to the 
    database and the ability to read and write tasks. It returns True if the 
    health check is successful, and False if any errors occur during the process.
    """
    def check_health(self):
        try:
            return self.load_tasks() is not None
        except Exception as e:
            logging.error(f"Health check failed with error: {e}")
            return False
        
    """
    Retrieves all tasks from the tasks_list.json file and returns them as a 
    list of Task objects.
     Returns:
        list[Task]: A list of Task objects retrieved from the database. 
    """
    def get_all_tasks(self) -> list[Task]:
        try:
            tasks = self.load_tasks()
            logging.info(f"Retrieved {len(tasks)} tasks successfully.")
            return tasks
        except Exception as e:
            logging.error(f"Failed to retrieve tasks with error: {e}")
            return []
        
    def set_done(self, task_id: int):
        try:
            tasks: list[Task] = self.load_tasks()
            for task in tasks:
                if task.id == task_id:
                    task.completed = True
                    logging.info(f"Task with id {task_id} marked as done.")
                    break
            self.save_tasks(tasks)
        except Exception as e:
            logging.error(f"Failed to mark task with id {task_id} as done with error: {e}")

    def set_undone(self, task_id: int):
        try:
            tasks: list[Task] = self.load_tasks()
            for task in tasks:
                if task.id == task_id:
                    task.completed = False
                    logging.info(f"Task with id {task_id} marked as undone.")
                    break
            self.save_tasks(tasks)
        except Exception as e:
            logging.error(f"Failed to mark task with id {task_id} as undone with error: {e}")

    def delete_task(self, task_id: int):
        try:
            tasks: list[Task] = self.load_tasks()
            tasks = [task for task in tasks if task.id != task_id]
            self.save_tasks(tasks)
            logging.info(f"Task with id {task_id} deleted successfully.")
        except Exception as e:
            logging.error(f"Failed to delete task with id {task_id} with error: {e}")

    def update_task(self, task_id: int, updated_task: Task):
        try:
            tasks: list[Task] = self.load_tasks()
            for i, task in enumerate(tasks):
                if task.id == task_id:
                    updated_task.id = task_id  # Ensure the ID remains unchanged
                    tasks[i] = updated_task
                    break
            self.save_tasks(tasks)
            logging.info(f"Task with id {task_id} updated successfully.")
        except Exception as e:
            logging.error(f"Failed to update task with id {task_id} with error: {e}")
        