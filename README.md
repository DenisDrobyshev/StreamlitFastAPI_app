# Система преобразования геодезических координат

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![SymPy](https://img.shields.io/badge/SymPy-1.12-3B5526?logo=sympy&logoColor=white)](https://www.sympy.org/)

Веб-сервис для пересчёта геодезических координат между референц-системами по **7-параметрической формуле Гельмерта**. Разделён на два независимых сервиса: FastAPI-бэкенд с вычислительным ядром и Streamlit-фронтенд для загрузки файлов и выгрузки результатов.

## Возможности

- 📥 Загрузка точек из **CSV** или **Excel** (`.xlsx`, `.xls`) с колонками `Name, X, Y, Z`.
- 🔄 Пересчёт между системами: **СК-42, СК-95, ПЗ-90, ПЗ-90.02, ПЗ-90.11, ГСК-2011, WGS-84 (G1150), ITRF-2008**.
- 🧮 Символьные вычисления через **SymPy** (матрица поворота + сдвиг + масштаб); параметры перехода хранятся в `parameters.json`.
- 📤 Выгрузка пересчитанных координат в **CSV**.
- 📝 Генерация **Markdown-отчёта** с формулами (LaTeX), примером расчёта первой точки, таблицей «до/после» и статистикой (mean, std).

## Архитектура

```
front (Streamlit)  ──HTTP──▶  back (FastAPI)
   app.py                        main.py
   загрузка файла                вычислительное ядро (SymPy)
   выбор систем                  parameters.json — параметры перехода
   скачивание CSV / .md          деплой: Render
```

Бэкенд задеплоен на **Render**: `https://streamlitfastapi-app.onrender.com`

### API

| Метод | Endpoint | Назначение |
|-------|----------|-----------|
| `POST` | `/convert-coordinates/` | Пересчёт координат, ответ — CSV-файл |
| `POST` | `/generate-report/` | Markdown-отчёт с формулами и статистикой |

Параметры запроса: `file` (CSV/Excel), `source_system`, `target_system`.

## Запуск локально

```bash
git clone https://github.com/DenisDrobyshev/StreamlitFastAPI_app.git
cd StreamlitFastAPI_app
pip install -r requirements.txt

# 1. Бэкенд
uvicorn back.main:app --reload --port 8000

# 2. Фронтенд (в отдельном терминале)
#    для локальной работы укажите BACKEND_URL = http://localhost:8000 в front/app.py
streamlit run front/app.py
```

## Структура

```
StreamlitFastAPI_app/
├── back/
│   ├── main.py          # FastAPI: эндпоинты, ядро преобразования, генерация отчёта
│   └── parameters.json  # параметры перехода между системами координат
├── front/
│   └── app.py           # Streamlit UI: загрузка, выбор систем, скачивание
└── requirements.txt
```

## Формат входного файла

| Name | X | Y | Z |
|------|-----|-----|-----|
| pt1  | 123456.789 | 234567.890 | 345678.901 |

## Стек

`FastAPI` · `Streamlit` · `pandas` · `SymPy` · `openpyxl` · `uvicorn` · `Render`
