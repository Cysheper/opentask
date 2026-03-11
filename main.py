import requests
from Scheduler.scheduler_core import Scheduler
from fastapi import FastAPI
from Modules.task import Task
from Modules.Log import logging
import uvicorn
from datetime import datetime
import json

app = FastAPI()

scheduler = Scheduler()

with open("./config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Task Scheduler API!"}

@app.get("/health")
def read_health():
    scheduler_health = scheduler.check_health()
    if scheduler_health:
        logging.info("Health check passed: Scheduler is healthy.")
        return {"status": "ok", "message": "Scheduler is healthy."}
    else:
        logging.error("Health check failed: Scheduler is not healthy.")
        return {"status": "error", "message": "Scheduler is not healthy."}

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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 