from Scheduler.scheduler_core import Scheduler
from fastapi import FastAPI, Query
from Modules.task import Task
from Modules.Log import logging, LOGGING_FILE_PATH
from datetime import datetime
import json
import pathlib

app: FastAPI = FastAPI()

scheduler: Scheduler = Scheduler()

with open("../config.json", "r", encoding="utf-8") as f:
    config: dict = json.load(f)

@app.get("/")
def read_root():
    return {"message": "Welcome to the OpenTask API!"}

@app.get("/health")
def read_health():
    scheduler_health = scheduler.check_health()
    if scheduler_health:
        logging.info("Health check passed: All systems are healthy.")
        return {"status": "ok", "message": "All systems are healthy."}
    else:
        logging.error("Health check failed: Some systems are not healthy. Please check the console for details.")
        return {"status": "error", "message": "Some systems are not healthy. Please check the console for details."}

@app.post("/add_task")
def add_task(task: dict):
    if not all(key in task for key in ("title", "code")):
        logging.error("Failed to add task: Missing required fields 'title' and 'code'")
        return {
            "status": "error",
            "message": "Missing required fields: 'title' and 'code'"
        }
    if "immediately" not in task and "trigger_time_list" not in task:
        logging.error("Failed to add task: Missing required fields 'immediately' or 'trigger_time_list'")
        return {
            "status": "error",
            "message": "Missing required fields: 'immediately' or 'trigger_time_list'"
        }
    
    try:
        new_task = Task(
            id=0,
            title=task["title"],
            description=task.get("description", ""),
            time=task.get("time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            code=task["code"],
            trigger_time_list=task.get("trigger_time_list", []),
            immediately=task.get("immediately", False),
            running=task.get("running", False),
            is_send=task.get("is_send", False),
            send_url=task.get("send_url", ""),
            send_token=task.get("send_token", "")
        )

        scheduler.add_task(new_task)
    except Exception as e:
        logging.error(f"Failed to add task with error: {e}")
        return {
            "status": "error",
            "message": f"Failed to add task: {e}"
        }
    
    logging.info(f"Task '{new_task.title}' added successfully")
    return {
        "status": "ok",
        "message": f"Task '{new_task.title}' added successfully"
    }

@app.get("/get_task/{task_id}")
def get_task(task_id: int):
    try:
        task = scheduler.get_task_by_id(task_id)
        if task:
            logging.info(f"Retrieved task with ID {task_id} successfully")
            return {
                "status": "ok",
                "task": task.to_dict()
            }
        else:
            logging.error(f"Task with ID {task_id} not found")
            return {
                "status": "error",
                "message": f"Task with ID {task_id} not found"
            }
    except Exception as e:
        logging.error(f"Failed to retrieve task with ID {task_id} with error: {e}")
        return {
            "status": "error",
            "message": f"Failed to retrieve task with ID {task_id}: {e}"
        }   


@app.get("/tasks")
def get_all_tasks():
    try:
        tasks = scheduler.get_all_tasks()
        logging.info(f"Retrieved {len(tasks)} tasks successfully")
        return {
            "status": "ok",
            "tasks": [task.to_dict() for task in tasks]
        }
    except Exception as e:
        logging.error(f"Failed to retrieve tasks with error: {e}")
        return {
            "status": "error",
            "message": f"Failed to retrieve tasks: {e}"
        }

@app.get("/set_done/{task_id}")
def set_done(task_id: int):
    try:
        existing_tasks = scheduler.get_all_tasks()
        existing_task = next((task for task in existing_tasks if task.id == task_id), None)
        if not existing_task:
            logging.error(f"Task with ID {task_id} not found for marking as done")
            return {
                "status": "error",
                "message": f"Task with ID {task_id} not found"
            }
        scheduler.set_done(task_id)
        logging.info(f"Task with ID {task_id} marked as done successfully")
        return {
            "status": "ok",
            "message": f"Task with ID {task_id} marked as done successfully"
        }
    except Exception as e:
        logging.error(f"Failed to mark task with ID {task_id} as done with error: {e}")
        return {
            "status": "error",
            "message": f"Failed to mark task with ID {task_id} as done: {e}"
        }
    
@app.get("/set_undone/{task_id}")
def set_undone(task_id: int):
    try:
        scheduler.set_undone(task_id)
        logging.info(f"Task with ID {task_id} marked as undone successfully")
        return {
            "status": "ok",
            "message": f"Task with ID {task_id} marked as undone successfully"
        }
    except Exception as e:
        logging.error(f"Failed to mark task with ID {task_id} as undone with error: {e}")
        return {
            "status": "error",
            "message": f"Failed to mark task with ID {task_id} as undone: {e}"
        }

@app.delete("/delete_task/{task_id}")
def delete_task(task_id: int):
    try:
        existing_tasks = scheduler.get_all_tasks()
        existing_task = next((task for task in existing_tasks if task.id == task_id), None)
        if not existing_task:
            logging.error(f"Task with ID {task_id} not found for deletion")
            return {
                "status": "error",
                "message": f"Task with ID {task_id} not found"
            }
        scheduler.delete_task(task_id)
        logging.info(f"Task with ID {task_id} deleted successfully")
        return {
            "status": "ok",
            "message": f"Task with ID {task_id} deleted successfully"
        }
    except Exception as e:
        logging.error(f"Failed to delete task with ID {task_id} with error: {e}")
        return {
            "status": "error",
            "message": f"Failed to delete task with ID {task_id}: {e}"
        }
    
@app.put("/update_task/{task_id}")
def update_task(task_id: int, updated_task: dict):
    try:
        existing_tasks = scheduler.get_all_tasks()
        existing_task = next((task for task in existing_tasks if task.id == task_id), None)
        if not existing_task:
            logging.error(f"Task with ID {task_id} not found for update")
            return {
                "status": "error",
                "message": f"Task with ID {task_id} not found"
            }
        
        updated_task_obj = Task(
            id=task_id,
            title=updated_task.get("title", existing_task.title),
            description=updated_task.get("description", existing_task.description),
            time=updated_task.get("time", existing_task.time),
            code=updated_task.get("code", existing_task.code),
            trigger_time_list=updated_task.get("trigger_time_list", existing_task.trigger_time_list),
            immediately=updated_task.get("immediately", existing_task.immediately),
            is_send=updated_task.get("is_send", existing_task.is_send),
            send_url=updated_task.get("send_url", existing_task.send_url),
            send_token=updated_task.get("send_token", existing_task.send_token)
        )

        scheduler.update_task(task_id, updated_task_obj)
        logging.info(f"Task with ID {task_id} updated successfully")
        return {
            "status": "ok",
            "message": f"Task with ID {task_id} updated successfully"
        }
    except Exception as e:
        logging.error(f"Failed to update task with ID {task_id} with error: {e}")
        return {
            "status": "error",
            "message": f"Failed to update task with ID {task_id}: {e}"
        }
    
@app.get("/get_console")
def get_logs(
    offset: int = Query(0, description="跳过多少条"),
    limit: int = Query(20, description="读取多少条")
):
    if not pathlib.Path(LOGGING_FILE_PATH).exists():
        return {"logs": [], "has_more": False}

    with open(LOGGING_FILE_PATH, "r", encoding="utf-8") as f:
        all_lines = f.readlines()
        # 假设我们想看最新的，所以从末尾开始算
        # 如果你想看最早的，就从头算
        total_count = len(all_lines)
        
        # 计算切片范围（这里以读取最早的为例）
        start = offset
        end = offset + limit
        
        selected_logs = all_lines[start:end]
        
        return {
            "logs": selected_logs,
            "has_more": end < total_count,
            "next_offset": end
        }
