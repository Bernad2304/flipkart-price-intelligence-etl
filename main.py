from fastapi import FastAPI, BackgroundTasks
import uuid
import csv
import os
import importlib.util
from datetime import datetime

app = FastAPI()
task_store = {}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXECUTION_LOG = os.path.join(BASE_DIR, "monitoring", "execution_history.csv")
METRICS_LOG = os.path.join(BASE_DIR, "monitoring", "pipeline_metrics.csv")


def load_module(module_name, file_path):
    """Loads a .py file as a usable module, even if its filename starts with a number
    (like '01_scrape_products.py'), which Python's normal import statement can't handle."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def log_execution(task_id, status, start_time, end_time, error_msg=""):
    os.makedirs(os.path.dirname(EXECUTION_LOG), exist_ok=True)
    file_exists = os.path.isfile(EXECUTION_LOG)
    with open(EXECUTION_LOG, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["task_id", "status", "start_time", "end_time", "error_message"])
        writer.writerow([task_id, status, start_time, end_time, error_msg])


def update_metrics(status):
    os.makedirs(os.path.dirname(METRICS_LOG), exist_ok=True)
    with open(METRICS_LOG, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["last_run_status", "last_run_time"])
        writer.writerow([status, datetime.now().isoformat()])


def run_pipeline(task_id: str):
    task_store[task_id]["status"] = "RUNNING"
    start_time = datetime.now().isoformat()
    try:
        scraper = load_module("scraper", os.path.join(BASE_DIR, "scripts", "01_scrape_products.py"))
        scraper.run_scraper()

        cleaner = load_module("cleaner", os.path.join(BASE_DIR, "scripts", "02_clean_data.py"))
        cleaner.run_cleaning()

        engineer = load_module("engineer", os.path.join(BASE_DIR, "scripts", "03_feature_engineering.py"))
        engineer.run_feature_engineering()

        task_store[task_id]["status"] = "SUCCESS"
        end_time = datetime.now().isoformat()
        log_execution(task_id, "SUCCESS", start_time, end_time)
        update_metrics("SUCCESS")
    except Exception as e:
        task_store[task_id]["status"] = "FAILED"
        end_time = datetime.now().isoformat()
        log_execution(task_id, "FAILED", start_time, end_time, str(e))
        update_metrics("FAILED")


@app.get("/")
def read_root():
    return {"message": "Hello Bernad, FastAPI is running!"}


@app.post("/run-etl")
def start_pipeline(background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    task_store[task_id] = {"status": "PENDING"}
    background_tasks.add_task(run_pipeline, task_id)
    return {"task_id": task_id, "status": "PENDING"}


@app.get("/etl-status/{task_id}")
def get_status(task_id: str):
    if task_id not in task_store:
        return {"error": "Task not found"}
    return {"task_id": task_id, "status": task_store[task_id]["status"]}