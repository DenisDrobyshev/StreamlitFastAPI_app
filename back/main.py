from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import pandas as pd
import os
import logging
import tempfile
from back.coordinate_transform import GSK_2011, generate_report_md

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="API для анализа координат")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Преобразование координат API работает",
        "endpoints": {
            "/process-csv/": "Загрузка и обработка CSV-файла с координатами и генерация Markdown-отчета"
        }
    }

@app.post("/process-csv/")
async def process_csv(file: UploadFile = File(...)):
    # Проверка расширения файла
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Требуется CSV-файл")

    # Создание временных файлов
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_input:
        input_path = tmp_input.name
        tmp_input.write(await file.read())

    output_md_path = tempfile.NamedTemporaryFile(delete=False, suffix=".md").name

    try:
        # Чтение CSV-файла
        print(f"Reading CSV from {input_path}")
        df = pd.read_csv(input_path)
        required_columns = ['Name', 'X', 'Y', 'Z']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(status_code=400, detail="CSV должен содержать колонки: Name, X, Y, Z")

        # Преобразование координат с помощью GSK_2011
        print("Calling GSK_2011")
        df_transformed = GSK_2011(
            sk1="СК-42",
            sk2="ГСК-2011",
            parameters_path="parameters.json",
            df=df,
            save_path=None
        )

        # Переименование колонок для generate_report_md
        print("Renaming columns")
        df_transformed = df_transformed.rename(columns={"X": "X_new", "Y": "Y_new", "Z": "Z_new"})

        print(f"Generating report at {output_md_path}")
        df_after = generate_report_md(
            df_before=df,  # Исходный DataFrame для отчета
            sk1="СК-42",
            sk2="ГСК-2011",
            parameters_path="parameters.json",
            md_path=output_md_path,
            csv_before=None,
            csv_after=None
        )

        print("Returning FileResponse")
        return FileResponse(
            output_md_path,
            media_type="text/markdown",
            filename="report.md"
        )

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка обработки: {str(e)}")
    

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)