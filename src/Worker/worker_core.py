from Modules.Log import logging
import requests
from Modules.task import Task
from pathlib import Path
import importlib.util
import sys
from queue import Queue
from multiprocessing import Process, Queue as MPQueue
from threading import Thread
from Tools.task_manager import TaskManager

class Worker:
    def __init__(self):
        self.save = TaskManager.save_tasks
        self.load = TaskManager.load_tasks

    def calculate(self, task: Task, q: Queue):
        logging.info("Starting task execution.")
        function_name = task.code.split(' ')[1].split('(')[0].strip()  # Extract function name from code
        
        file_path = Path(f"./Tasks/{function_name}.py")
        file_path.write_text(task.code)  # Write the code to a *.py file
        spec = importlib.util.spec_from_file_location(function_name, file_path)

        if spec is None or spec.loader is None:
            logging.error(f"Failed to create module spec for {function_name}.py")
            return None
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)  # Load the module
            func = getattr(module, function_name)  # Get the function from the module
            result = func()  # Execute the function and get the result
            q.put(result)  # Put the result in the queue to send it back to the parent process
        except Exception as e:
            logging.error(f"Failed to execute module {function_name}.py with error: {e}")
            return None
        finally:
            if file_path.exists(): file_path.unlink()
            sys.modules.pop(function_name, None)

    def clean(self, function_name: str):
        """父进程侧清理：kill 子进程后调用，路径在父进程中计算，不依赖子进程的内存状态"""
        file_path = Path(f"./Tasks/{function_name}.py")
        if file_path.exists():
            file_path.unlink()
            logging.info(f"Cleaned up temporary file: {file_path}")
        sys.modules.pop(function_name, None)

    def push(self, task: Task) -> None:
        try:
            Thread(target=self.run, args=(task,), daemon=True).start()
        except Exception as e:
            logging.error(f"Failed to start thread for task {task.title} with error: {e}")  

    def run(self, task: Task) -> None:
        function_name = task.code.split(' ')[1].split('(')[0].strip()
        try:
            q = MPQueue()  # Use multiprocessing Queue for inter-process communication
            p = Process(target=self.calculate, args=(task, q), daemon=True)
            p.start()
            
            # Wait for the process to finish or timeout 
            timeout = task.timeout

            if timeout is None:
                p.join()  # Wait indefinitely if no timeout is specified
            else:
                p.join(timeout=timeout)

            if p.is_alive():
                logging.warning(f"{task.title} execution exceeded timeout of {timeout} seconds.")
                p.kill() # Terminate the process if it's still alive after timeout
                p.join() # Wait for the process to be fully terminated
                self.clean(function_name)  # 在父进程侧清理，路径由父进程自己计算
                return None

            result = q.get() if not q.empty() else None

            logging.info(f"Task executed successfully with result: {result}")
            if task.is_send:
                self.send_result(result, task)

        except Exception as e:
            logging.error(f"Task execution failed with error: {e}")


    def send_result(self, result, task: Task):
        try:
            if not task.send_url or not task.send_token:
                logging.warning(f"Task {task.title} is marked to send result but missing send_url or send_token.")
                return
            logging.info(f"Sending result to {task.send_url}")
            response = requests.post(task.send_url, json={"msg": result}, headers={"Authorization": f"Bearer {task.send_token}"})
            response.raise_for_status()
            logging.info(f"Result sent successfully to {task.send_url}, response: {response.text}")
        except requests.RequestException as e:
            logging.error(f"Failed to send result to {task.send_url} with error: {e}")

