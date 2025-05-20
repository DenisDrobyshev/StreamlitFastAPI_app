from fastapi import FastAPI, UploadFile, File, HTTPException, Query
import pandas as pd
import json
from sympy import symbols, Matrix, N, latex
from datetime import datetime
from io import BytesIO
import base64
from fastapi.middleware.cors import CORSMiddleware
import logging

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

def load_parameters(path="parameters.json"):
    """Загружает параметры из JSON"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise ValueError(f"Ошибка чтения параметров: {str(e)}")

def GSK_2011(sk1, sk2, parameters_path, df=None):
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
        raise ValueError(f"Система {sk1} не найдена в {parameters_path}")

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

    if df is None:
        raise ValueError("Нужно передать DataFrame")

    transformed = []

    for _, row in df.iterrows():
        elements = {
            **elements_const,
            X: row["X"],
            Y: row["Y"],
            Z: row["Z"],
        }

        results_vector = formula.subs(elements).applyfunc(N)
        transformed.append([
            row["Name"],
            float(results_vector[0]),
            float(results_vector[1]),
            float(results_vector[2]),
        ])

    df_result = pd.DataFrame(transformed, columns=["Name", "X", "Y", "Z"])

    return df_result

def generate_report_md(df_before, sk1, sk2, parameters_path, md_path):
    ΔX, ΔY, ΔZ, ωx, ωy, ωz, m = symbols('ΔX ΔY ΔZ ωx ωy ωz m')
    X, Y, Z = symbols('X Y Z')
    general_formula = (1 + m) * Matrix([[1, ωz, -ωy], [-ωz, 1, ωx], [ωy, -ωx, 1]]) @ Matrix([[X], [Y], [Z]]) + Matrix([[ΔX], [ΔY], [ΔZ]])

    with open(parameters_path, 'r', encoding='utf-8') as f:
        params = json.load(f)
    p = params.get(sk1)
    if p is None:
        raise ValueError(f"Система {sk1} не найдена в {parameters_path}")
    subs_common = {
        ΔX: p["ΔX"], ΔY: p["ΔY"], ΔZ: p["ΔZ"],
        ωx: p["ωx"], ωy: p["ωy"], ωz: p["ωz"],
        m: p["m"] * 1e-6
    }

    rows = []
    for _, r in df_before.iterrows():
        subs = {**subs_common, X: r["X"], Y: r["Y"], Z: r["Z"]}
        rv = general_formula.subs(subs).applyfunc(N)
        rows.append({
            "Name": r["Name"],
            "X_new": float(rv[0]),
            "Y_new": float(rv[1]),
            "Z_new": float(rv[2])
        })
    df_after = pd.DataFrame(rows)

    with open(md_path, 'w', encoding='utf-8') as md:
        md.write("# Отчёт по преобразованию координат\n")
        md.write(f"**Исходная система**: {sk1}\n")
        md.write(f"**Конечная система**: {sk2}\n\n")

        md.write("## 1. Общая формула\n\n")
        md.write(f"$$\n{latex(general_formula)}\n$$\n\n")

        md.write("## 2. Формула с подстановкой параметров\n\n")
        formula_p = general_formula.subs(subs_common)
        md.write(f"$$\n{latex(formula_p)}\n$$\n\n")

        md.write("## 3. Пример для первой точки\n\n")
        first = df_before.iloc[0]
        md.write(f"- Исходные: $X={first['X']},\\;Y={first['Y']},\\;Z={first['Z']}$\n")
        subs1 = {**subs_common, X: first["X"], Y: first["Y"], Z: first["Z"]}
        f3 = general_formula.subs(subs1)
        f3n = f3.applyfunc(N)
        md.write(f"- Подстановка в формулу:\n  $$\n{latex(f3)}\n$$\n")
        md.write(f"- Численный результат: $X'={f3n[0]},\\;Y'={f3n[1]},\\;Z'={f3n[2]}$\n\n")

        md.write("## 4. Таблица до и после и статистика\n\n")

        md.write("| Name | X | Y | Z | X' | Y' | Z' |\n")
        md.write("|---|---|---|---|---|---|---|\n")
        for b,a in zip(df_before.itertuples(), df_after.itertuples()):
            md.write(f"|{b.Name}|{b.X:.6f}|{b.Y:.6f}|{b.Z:.6f}"
                     f"|{a.X_new:.6f}|{a.Y_new:.6f}|{a.Z_new:.6f}|\n")

        md.write("\n**Статистика (X', Y', Z'):**\n\n")
        stats = df_after[["X_new","Y_new","Z_new"]].agg(["mean","std"])
        for idx in stats.index:
            s = stats.loc[idx]
            md.write(f"- {idx}: X'={s['X_new']:.3f}, Y'={s['Y_new']:.3f}, Z'={s['Z_new']:.3f}\n")

    return df_after


@app.get("/systems")
async def get_systems():
    try:
        with open("parameters.json", "r", encoding="utf-8") as f:
            params = json.load(f)
        return {"systems": list(params.keys())}
    except Exception as e:
        return {"error": str(e), "systems": []}
    
@app.post("/transform")
async def transform_file(
    file: UploadFile = File(...),
    sk1: str = Query(..., description="Исходная система координат"),
    sk2: str = Query(..., description="Целевая система координат")
):
    try:
        # Чтение файла
        file_data = await file.read()
        df = pd.read_excel(BytesIO(file_data))

        # Проверка столбцов
        required_columns = ["Name", "X", "Y", "Z"]
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(status_code=400, detail=f"Файл должен содержать колонки: {required_columns}")

        # Загрузка параметров
        parameters_path = "parameters.json"
        params = load_parameters(parameters_path)

        # Проверка наличия путей
        if sk1 not in params or sk2 not in params:
            raise HTTPException(status_code=400, detail="Одна из систем координат не найдена в параметрах")

        # Преобразование
        df_transformed = GSK_2011(sk1, sk2, parameters_path, df=df)

        # Генерация отчета
        report_path = "report.md"
        df_report = generate_report_md(df, sk1, sk2, parameters_path, report_path)

        # Сохранение данных и отчета
        output = BytesIO()
        df_transformed.to_excel(output, index=False)
        output.seek(0)

        with open(report_path, "r", encoding="utf-8") as f:
            report_content = f.read()

        return {
            "status": "success",
            "data": base64.b64encode(output.read()).decode(),
            "report": report_content
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)