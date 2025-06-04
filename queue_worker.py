import os
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Dict
from runner import run_checker   # already implemented

# ------------- configuration -----------------
MAX_WORKERS = 5          # <= 5 parallel sandboxes ~ fine for 300 students
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)
# ---------------------------------------------

executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
jobs: Dict[str, Future] = {}           # job_id -> Future

def enqueue(source_cpp: str, lab_id: str) -> str:
    """Submit a job, return its id."""
    import uuid, shutil
    job_id = str(uuid.uuid4())

    # copy student file into results dir (frozen snapshot)
    dst_cpp = os.path.join(RESULTS_DIR, job_id + ".cpp")
    shutil.copy2(source_cpp, dst_cpp)

    fut = executor.submit(_worker, dst_cpp, lab_id, job_id)
    jobs[job_id] = fut
    return job_id

def _worker(cpp_path: str, lab: str, job_id: str) -> str:
    """Background thread – run tests and save report."""
    report = run_checker(cpp_path, lab)
    out_file = os.path.join(RESULTS_DIR, job_id + ".txt")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(report)
    return report

def get_status(job_id: str):
    fut = jobs.get(job_id)
    if not fut:
        return "UNKNOWN"
    if fut.done():
        return "READY"
    return "RUNNING"

def get_report(job_id: str) -> str:
    path = os.path.join(RESULTS_DIR, job_id + ".txt")
    if os.path.exists(path):
        return open(path, encoding="utf-8").read()
    return "[WAIT] still running …"
