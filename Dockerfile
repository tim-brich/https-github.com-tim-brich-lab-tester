# ---- Dockerfile ----
FROM gcc:12

WORKDIR /opt/autotester_project
COPY checker.cpp .

# Компилируем checker один раз при сборке образа
RUN g++ -std=c++17 checker.cpp -o checker

ENTRYPOINT ["/opt/autotester_project/checker"]
# ---------------------
