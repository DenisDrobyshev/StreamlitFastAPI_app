from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import StreamingResponse
from io import BytesIO
import pandas as pd
import json
import csv
import random
import string
from sympy import Matrix, symbols, N
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

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
def generate_csv(file_path: str, num_rows: int):
    def random_name(length=5):
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for _ in range(length))
    def random_number():
        return random.randint(100000000, 999999000) / 1000
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'X', 'Y', 'Z'])
        for _ in range(num_rows):
            writer.writerow([random_name(), random_number(), random_number(), random_number()])


def create_default_parameters(file_path: str = "parameters.json"):
    parameters = {
        "СК-42": {
            "ΔX": 23.56,
            "ΔY": -140.86,
            "ΔZ": -79.77,
            "ωx": -8.423e-09,
            "ωy": -1.678e-06,
            "ωz": -3.849e-06,
            "m": -0.2274
        },
        "СК-95": {
            "ΔX": 24.46,
            "ΔY": -130.80,
            "ΔZ": -81.53,
            "ωx": -8.423e-09,
            "ωy": 1.724e-08,
            "ωz": -6.511e-07,
            "m": -0.2274
        },
        "ПЗ-90": {
            "ΔX": -1.443,
            "ΔY": 0.142,
            "ΔZ": 0.230,
            "ωx": -8.423e-09,
            "ωy": 1.724e-08,
            "ωz": -6.511e-07,
            "m": -0.2274
        },
        "ПЗ-90.02": {
            "ΔX": -0.373,
            "ΔY": 0.172,
            "ΔZ": 0.210,
            "ωx": -8.423e-09,
            "ωy": 1.724e-08,
            "ωz": -2.061e-08,
            "m": -0.0074
        },
        "ПЗ-90.11": {
            "ΔX": 0.0,
            "ΔY": -0.014,
            "ΔZ": 0.008,
            "ωx": 2.724e-09,
            "ωy": 9.212e-11,
            "ωz": -2.566e-10,
            "m": 0.0006
        },
        "ГСК-2011": {
            "ΔX": 0,
            "ΔY": 0,
            "ΔZ": 0,
            "ωx": 0,
            "ωy": 0,
            "ωz": 0,
            "m": 0
        }
    }
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(parameters, f, ensure_ascii=False, indent=4)

def GSK_2011(sk1: str, sk2: str, parameters_path: str, df: pd.DataFrame, save_path: Optional[str] = None) -> pd.DataFrame:
    if sk1 == "СК-95" and sk2 == "СК-42":
        df_temp = GSK_2011("СК-95", "ПЗ-90.11", parameters_path, df=df)
        df_result = GSK_2011("ПЗ-90.11", "СК-42", parameters_path, df=df_temp)
        return df_result

    ΔX, ΔY, ΔZ, ωx, ωy, ωz, m = symbols('ΔX ΔY ΔZ ωx ωy ωz m')
    X, Y, Z = symbols('X Y Z')

    formula = (1 + m) * Matrix([[1, ωz, -ωy], [-ωz, 1, ωx], [ωy, -ωx, 1]]) @ Matrix([[X], [Y], [Z]]) + Matrix([[ΔX], [ΔY], [ΔZ]])

    with open(parameters_path, 'r', encoding='utf-8') as f:
        parameters = json.load(f)

    if sk1 not in parameters:
        raise ValueError(f"Исходная система '{sk1}' отсутствует в параметрах")

    param = parameters[sk1]
    elements_const = {
        ΔX: param["ΔX"],
        ΔY: param["ΔY"],
        ΔZ: param["ΔZ"],
        ωx: param["ωx"],
        ωy: param["ωy"],
        ωz: param["ωz"],
        m: param["m"] * 1e-6
    }

    transformed = []
    for _, row in df.iterrows():
        elements = {
            X: row["X"],
            Y: row["Y"],
            Z: row["Z"],
            **elements_const
        }
        results_vector = formula.subs(elements).applyfunc(N)
        transformed.append([
            row["Name"],
            float(results_vector[0]),
            float(results_vector[1]),
            float(results_vector[2]),
        ])

    df_result = pd.DataFrame(transformed, columns=["Name", "X", "Y", "Z"])
    if save_path:
        df_result.to_csv(save_path, index=False)
    return df_result

def generate_markdown_report(df_before: pd.DataFrame, df_after: pd.DataFrame, source_system: str, target_system: str) -> str:
    report = "# Отчёт по преобразованию координат\n"
    report += f"Исходная система: {source_system}\n"
    report += f"Конечная система: {target_system}\n\n"

    report += "## 1. Общая формула\n"
    report += "$$ \n"
    report += r"\begin{bmatrix} X' \\ Y' \\ Z' \end{bmatrix} = (1 + m) \cdot " \
              r"\begin{bmatrix} 1 & \omega_z & -\omega_y \\ -\omega_z & 1 & \omega_x \\ \omega_y & -\omega_x & 1 \end{bmatrix} \cdot " \
              r"\begin{bmatrix} X \\ Y \\ Z \end{bmatrix} + " \
              r"\begin{bmatrix} \Delta X \\ \Delta Y \\ \Delta Z \end{bmatrix}"
    report += "\n$$\n\n"


    report += "## 2. Формула с подстановкой параметров\n"
    report += "$$ \n"
    report += r"\begin{bmatrix} X' \\ Y' \\ Z' \end{bmatrix} = " \
              r"\begin{bmatrix} 0.9999997726 X - 3.8489991247374 \cdot 10^{-6} Y + 1.6779996184228 \cdot 10^{-6} Z + 23.56 \\ " \
              r"3.8489991247374 \cdot 10^{-6} X + 0.9999997726 Y - 8.4229980846098 \cdot 10^{-9} Z - 140.86 \\ " \
              r"-1.6779996184228 \cdot 10^{-6} X + 8.4229980846098 \cdot 10^{-9} Y + 0.9999997726 Z - 79.77 \end{bmatrix}"
    report += "\n$$\n\n"

    first_before = df_before.iloc[0]
    first_after = df_after.iloc[0]
    report += "## 3. Пример для первой точки\n"
    report += "Исходные: $X=%.6f,\\;Y=%.6f,\\;Z=%.6f$\n" % (
        first_before['X'], first_before['Y'], first_before['Z'])
    report += "$$ \n"
    report += r"\begin{bmatrix} %.6f \\ %.6f \\ %.6f \end{bmatrix}" % (
        first_after['X'], first_after['Y'], first_after['Z'])
    report += "\n$$\n"
    report += "Численный результат: $X'=%.6f,\\;Y'=%.6f,\\;Z'=%.6f$\n\n" % (
        first_after['X'], first_after['Y'], first_after['Z'])

    report += "## 4. Таблица до и после и статистика\n"
    report += "| Name | X | Y | Z | X' | Y' | Z' |\n"
    report += "| --- | --- | --- | --- | --- | --- | --- |\n"
    for i in range(min(10, len(df_before))):
        b = df_before.iloc[i]
        a = df_after.iloc[i]
        report += f"| {b['Name']} | {b['X']:.6f} | {b['Y']:.6f} | {b['Z']:.6f} | {a['X']:.6f} | {a['Y']:.6f} | {a['Z']:.6f} |\n"
    report += "\n"

    report += "## Статистика (X', Y', Z')\n"
    report += "- mean: X'=%.3f, Y'=%.3f, Z'=%.3f\n" % (
        df_after['X'].mean(), df_after['Y'].mean(), df_after['Z'].mean())
    report += "- std: X'=%.3f, Y'=%.3f, Z'=%.3f\n" % (
        df_after['X'].std(), df_after['Y'].std(), df_after['Z'].std())

    return report

@app.post("/convert-coordinates/")
async def convert_coordinates(
    file: UploadFile = File(...),
    source_system: str = Form("СК-42"),
    target_system: str = Form("ГСК-2011")
):
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Поддерживаются только .csv или .xlsx/.xls")

    try:
        contents = await file.read()
        input_path = "input.csv"
        output_path = "converted.csv"
        parameters_path = "parameters.json"

        if file.filename.endswith(".csv"):
            df = pd.read_csv(BytesIO(contents))
        else:
            df = pd.read_excel(BytesIO(contents))

        required_columns = ["Name", "X", "Y", "Z"]
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(status_code=400, detail=f"Файл должен содержать колонки: {required_columns}")

        create_default_parameters(parameters_path)
        result_df = GSK_2011(sk1=source_system, sk2=target_system, parameters_path=parameters_path, df=df, save_path=output_path)

        output = BytesIO()
        result_df.to_csv(output, index=False)
        output.seek(0)

        filename = f"converted_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке: {str(e)}")

@app.post("/generate-report/")
async def generate_report(
    file: UploadFile = File(...),
    source_system: str = Form("СК-42"),
    target_system: str = Form("ГСК-2011")
):
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Поддерживаются только .csv или .xlsx/.xls")

    try:
        contents = await file.read()
        input_path = "input.csv"
        parameters_path = "parameters.json"

        if file.filename.endswith(".csv"):
            df = pd.read_csv(BytesIO(contents))
        else:
            df = pd.read_excel(BytesIO(contents))

        required_columns = ["Name", "X", "Y", "Z"]
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(status_code=400, detail=f"Файл должен содержать колонки: {required_columns}")

        create_default_parameters(parameters_path)
        result_df = GSK_2011(sk1=source_system, sk2=target_system, parameters_path=parameters_path, df=df.copy())

        markdown_report = generate_markdown_report(df, result_df, source_system, target_system)
        output = BytesIO(markdown_report.encode('utf-8'))
        output.seek(0)

        filename = f"report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.md"
        return StreamingResponse(
            output,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при формировании отчёта: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)