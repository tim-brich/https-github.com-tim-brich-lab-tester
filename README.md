# Lab Tester — Полное руководство (с публикацией через Cloudpub)

---

## 🧠 Описание проекта

**Lab Tester** — это система автоматической проверки лабораторных работ по C++:

- Студент загружает `.cpp` через веб-форму.
- Код компилируется и прогоняется по тестам в изолированном Docker-контейнере.
- Система возвращает отчёт:
  ```
  [COMPILATION SUCCESS]
  [TEST 1] Passed
  …
  [SUMMARY] n / m tests passed
  ```
- Платформа безопасна: сеть отключена, память и CPU ограничены, файловая система read-only (кроме `/w`).

---

## 📁 Структура проекта

```
lab-tester/
├── app.py                  ← Flask-приложение
├── runner.py               ← Запуск контейнера
├── queue_worker.py         ← Очередь задач (воркеры)
├── checker.cpp             ← Утилита проверки
├── Dockerfile              ← Docker-образ с checker
├── requirements.txt        ← Зависимости (Flask)
│
├── tests/                  ← Тесты (по лабораторным)
│   └── lab1/
│       ├── input1.txt
│       └── output1.txt
├── uploads/                ← Автосоздаётся (временные .cpp)
└── results/                ← Автосоздаётся (отчёты, копии кода)
```

---

## ⚙️ Требования

| Компонент           | Версия     | Проверка                        |
|---------------------|------------|---------------------------------|
| Windows             | 10 / 11    |                                 |
| Python              | ≥ 3.8      | `python --version`              |
| Docker Desktop      | ≥ 4.x      | `docker --version`              |
| Git                 | любой      | `git --version`                 |
| Cloudpub            | аккаунт    | cloudpub.ru                     |

---

## 📦 Клонирование проекта

```cmd
cd C:\
git clone https://github.com/tim-brich/https-github.com-tim-brich-lab-tester.git lab-tester
cd lab-tester
```

---

## 🐍 Настройка Python-окружения

```cmd
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

---

## 🐳 Сборка Docker-образа

```cmd
docker build -t autotester_project-sandbox .
```

Ожидаем сообщение `Successfully tagged autotester_project-sandbox`.

---

## 📂 Проверка доступа Docker к диску

```cmd
docker run --rm -v %cd%:/data ubuntu cmd /C "dir /data"
```

Если всплывёт окно **File Sharing**, нажмите **Share**.

---

## 🚀 Запуск Flask-приложения

```cmd
python app.py
```

В консоли появится:
```
Running on http://127.0.0.1:5000/
```

---

## 🌐 Проверка через браузер

1. Откройте `http://localhost:5000`
2. Заполните форму:
   - `Student name`: любое
   - `Lab ID`: `lab1`
   - Загрузите `.cpp`, например:
     ```cpp
     #include <iostream>
     using namespace std;
     int main() {
         int x;
         cin >> x;
         cout << x * 2 << endl;
         return 0;
     }
     ```
3. Нажмите **Submit**  
4. Вас перекинет на `/job/<job_id>`  
   Через несколько секунд появится:
   ```
   [COMPILATION SUCCESS]
   [TEST 1] Passed
   [SUMMARY] 1 / 1 tests passed
   ```

---

## 🧪 Проверка лимитов контейнера

1. В `runner.py` временно удалите `"--rm",`
2. Выполните тест
3. Откройте новое окно CMD:

```cmd
docker ps -a
docker inspect <ID> | findstr /C:"Memory" /C:"NanoCpus" /C:"PidsLimit"
```

Вы должны увидеть:
- Memory: `268435456` (256 MB)
- NanoCpus: `500000000` (0.5 CPU)
- PidsLimit: `128`

4. Верните `"--rm",` обратно и перезапустите Flask

---

## 🛠 Изменение лимитов и параметров

В `runner.py`:

```python
MEM_LIMIT  = "256m"
CPU_LIMIT  = "0.5"
PIDS_LIMIT = "128"
TIMEOUT    = 20
```

Также:

```python
"--tmpfs", "/w:rw,exec,size=64m",
```

Измените → сохраните → перезапустите `python app.py`.  
Docker-образ пересобирать **не нужно**.

---

## 🌍 Публикация через Cloudpub

> Cloudpub позволяет открыть `localhost:5000` по HTTPS-домену без проброса портов.

### 🔐 Шаг 1 — регистрация

1. Перейдите на [https://cloudpub.ru](https://cloudpub.ru)
2. Зарегистрируйтесь
3. Создайте туннель:  
   - Название: `lab-tester`
   - Порт: `5000`
   - Протокол: `HTTP`
   - Категория: `Flask`
   - Назначьте любой публичный поддомен

### 🌐 Шаг 2 — запуск туннеля

1. Установите агент Cloudpub:  
   [https://cloudpub.ru/install](https://cloudpub.ru/install)

2. Запустите его (автоматически или вручную)

3. В панели Cloudpub нажмите «Подключить» к вашему туннелю  
   → появится статус **"online"**

4. Откройте `https://<your-subdomain>.cloudpub.ru`  
   — вы увидите веб-форму автотестера

> Теперь студентам не нужно подключение по локальной сети.  
> Вы можете оставить Flask-сервер запущенным локально — Cloudpub будет передавать запросы.

---

## 🧯 Частые ошибки и их решения

| Ошибка                                 | Причина                                   | Решение                                                        |
|----------------------------------------|-------------------------------------------|----------------------------------------------------------------|
| `compile_errors.txt: Read-only FS`     | checker пишет в корень                    | Убедитесь: `--tmpfs /w:rw,exec,size=64m`, `-w /w`              |
| `student_program.exe: not found`       | нет `./` при запуске                      | В `checker.cpp`: `./` перед `exe_path`                         |
| `Permission denied`                    | tmpfs без exec                            | В `runner.py`: `--tmpfs /w:rw,exec,size=64m`                   |
| `Failed at line 1` при правильном выводе | CRLF в эталонах                          | В `checker.cpp` уже удаляется `\r`                             |
| Страница зависает на RUNNING           | задача зависла или не стартовала          | Проверьте `runner.py`, увеличьте `TIMEOUT`, смотрите консоль  |

---

## ✅ Завершение

Теперь вы можете:
- Работать локально по адресу `http://localhost:5000`
- Подключать Cloudpub и принимать `.cpp` от студентов из интернета
- Безопасно изолировать код в Docker-контейнерах с ограничениями

🎉 Удачи!
