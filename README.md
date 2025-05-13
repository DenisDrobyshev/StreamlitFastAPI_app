# **Coordinate Analysis System**  

🚀 **Система анализа координат** — это веб-приложение для автоматической обработки Excel-файлов с координатами.  
**Функционал**:  
- 📊 Генерация статистики (среднее, медиана, отклонение и др.)  
- 📈 Визуализация данных (графики, гистограммы, 3D-диаграммы)  
- 📥 Скачивание отчетов в Word и Markdown  
- 🌐 Полностью облачный стек: FastAPI (бэкенд) + Streamlit (фронтенд)  

**Демо**:  
🔹 **Фронтенд**: [Streamlit App](https://your-streamlit-app.onrender.com)  
🔹 **Бэкенд**: `https://your-fastapi-app.onrender.com`  

---

## **Содержание**  
1. [Функционал](#-функционал)  
2. [Технологии](#-технологии)  
3. [Быстрый старт](#-быстрый-старт)  
4. [API Endpoints](#-api-endpoints)  
5. [Разработка](#-разработка)  
6. [Лицензия](#-лицензия)  

---

## ✨ **Функционал**  
- **Загрузка Excel-файлов** (XLSX/XLS/CSV) с колонками `x`, `y`, `z`  
- **Статистический анализ**:  
  - Среднее, медиана, стандартное отклонение  
  - Минимальные/максимальные значения  
- **Визуализация**:  
  - Гистограммы распределения  
  - Boxplot  
  - 3D-диаграмма рассеяния  
- **Экспорт отчетов**:  
  - 📄 Markdown  
  - 📝 Word (DOCX)  

---

## 🛠 **Технологии**  
| Компонент       | Технологии                                                                 |  
|-----------------|---------------------------------------------------------------------------|  
| **Бэкенд**      | FastAPI, Uvicorn, Pandas, Matplotlib, python-docx                        |  
| **Фронтенд**    | Streamlit, Requests                                                      |  
| **Деплой**      | Render (бэкенд), Streamlit Cloud (фронтенд)                              |  
| **Аналитика**   | NumPy, SciPy                                                             |  

---

## 🚀 **Быстрый старт**  
### 1. Клонирование репозитория  
```bash  
git clone https://github.com/DenisDrobyshev/StreamlitFastAPI_app  
cd StreamlitApp
```  

### 2. Установка зависимостей  
```bash  
pip install -r requirements.txt  
```  

### 3. Запуск локально  
**Бэкенд**:  
```bash  
uvicorn back.main:app --reload  
```  
→ Документация API: `http://localhost:8000/docs`  

**Фронтенд**:  
```bash  
streamlit run front/app.py  
```  
→ Приложение: `http://localhost:8501`  

---

## 🌐 **API Endpoints**  
| Метод | Эндпоинт       | Описание                          |  
|-------|----------------|-----------------------------------|  
| `GET` | `/`            | Проверка работоспособности API    |  
| `POST`| `/analyze`     | Анализ файла с координатами       |  

**Пример запроса**:  
```bash  
curl -X POST -F "file=@coordinates.xlsx" https://your-api.onrender.com/analyze  
```  

**Ответ**:  
```json  
{  
  "statistics": {  
    "mean": {"x": 100.5, "y": 200.3, "z": 50.7},  
    "plots_base64": "base64-encoded-image",  
    "markdown_report": "# Отчет...",  
    "word_report": "base64-encoded-docx"  
  }  
}  
```  

---

## 🔧 **Разработка**  
### Правила внесения изменений:  
1. Форматируйте код через `black`:  
```bash  
black .  
```  
2. Тестируйте изменения:  
```bash  
pytest tests/  
```  
3. Линтинг:  
```bash  
flake8 .  
```  

### Деплой:  
1. **Render** (бэкенд):  
   - Укажите команду запуска: `uvicorn back.main:app --host 0.0.0.0 --port $PORT`  
2. **Streamlit Cloud** (фронтенд):  
   - Загрузите `front/app.py` и `requirements.txt`  

---

## 🐛 **Типовые ошибки**  
| Ошибка                          | Решение                                |  
|---------------------------------|---------------------------------------|  
| `Missing columns x, y, z`      | Проверьте заголовки в Excel-файле     |  
| `File too large (max 5MB)`     | Уменьшите размер файла                |  
| `500 Internal Server Error`    | Смотрите логи на Render               |  

---



> **Примечание**: Для работы с Word-отчетами требуется Microsoft Word или совместимый редактор.