import subprocess
from pathlib import Path

SANDBOX_IMAGE = "autotester_project-sandbox"

MEM_LIMIT  = "256m"   # Ограничение памяти (256 МБ)
CPU_LIMIT  = "0.5"    # Половина CPU
PIDS_LIMIT = "128"    # Максимум процессов внутри контейнера
TIMEOUT    = 20       # Лимит времени выполнения (секунды)

def run_checker(source_path: str, lab_id: str) -> str:
    src_abs   = Path(source_path).resolve()
    tests_abs = (Path(__file__).parent / "tests").resolve()

    if not src_abs.exists():
        return "[ERROR] Source file not found."

    cmd = [
        "docker", "run", "--rm",

        # --- жёсткие ограничения ---
        "--network", "none",
        "--read-only",                  # корень контейнера по-прежнему только-чтение
        "--pids-limit", PIDS_LIMIT,
        "--memory", MEM_LIMIT,
        "--cpus", CPU_LIMIT,
        "--security-opt", "no-new-privileges",
        "--cap-drop", "ALL",

        # --- единственное место, куда можно писать ---
        "--tmpfs", "/w:rw,exec,size=64m",    # создаём tmpfs (/w) объёмом 64 МБ
        "-w", "/w",                     # рабочая директория = /w

        # --- монтируем файлы ---
        # сам .cpp читается только-чтение
        "-v", f"{src_abs}:/w/student.cpp:ro",
        # тесты тоже только-чтение
        "-v", f"{tests_abs}:/w/tests:ro",

        SANDBOX_IMAGE,
        "/w/student.cpp", lab_id        # аргументы для checker
]


    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=TIMEOUT
        )
    except subprocess.TimeoutExpired:
        return "[ERROR] Execution timed out."

    out = proc.stdout.decode("utf-8", errors="replace")
    err = proc.stderr.decode("utf-8", errors="replace")
    if err.strip():
        out += "\n[STDERR]\n" + err
    return out or "[ERROR] No output produced."
