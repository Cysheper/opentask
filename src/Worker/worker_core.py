from Modules.Log import logging
import requests
from Modules.task import Task
from pathlib import Path
import importlib.util
import sys
from multiprocessing import Process, Queue


class Worker:
    def __init__(self):
        pass

    """
    Executes the code associated with a given task in a separate process to ensure isolation and prevent blocking the main thread.
     - The code is written to a temporary Python file named after the function being executed.
     - The function is then imported and executed, with the result sent back to the parent process via a multiprocessing Queue.
     - After execution, the temporary file is deleted and the module is removed from sys.modules to clean up the environment.
     - If the task is marked to send results, the result is sent to the specified URL with the provided token for authentication.
     - The method also handles timeouts and logs relevant information and errors throughout the execution process.
    """
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
        
    def run(self, task: Task, timeout: int | None = None) -> None:
        from main import config
        if timeout is None:
            timeout = config.get("timeout", 60)
        try:
            q = Queue()
            p = Process(target=self.calculate, args=(task, q))
            p.start()
            
            # Wait for the process to finish or timeout
            p.join(timeout=timeout)
            
            if p.is_alive():
                logging.warning(f"Task execution exceeded timeout of {timeout} seconds. Terminating process.")
                p.terminate()
                p.join()
                return None

            result = q.get() if not q.empty() else None

            logging.info(f"Task executed successfully with result: {result}")
            if task.is_send:
                self.send_result(result, task)

        except Exception as e:
            logging.error(f"Task execution failed with error: {e}")
