import streamlit as st
import pandas as pd
import requests
from io import BytesIO
from urllib.parse import urljoin

BACKEND_URL = "https://streamlitfastapi-app.onrender.com"

st.set_page_config(page_title="Преобразование координат", layout="wide")
st.title("Система преобразования координат")
st.markdown("Загрузите CSV-файл со столбцами name, x, y, z для преобразования.")

COORD_SYSTEMS = [
    "СК-42", "СК-95", "ПЗ-90", "ПЗ-90.02", "ПЗ-90.11",
    "WGS-84 (G1150)", "ITRF-2008", "ГСК-2011"
]

def check_api_status():
    try:
        response = requests.get(BACKEND_URL, timeout=10)
        return response.status_code == 200
    except requests.RequestException:
        return False

def convert_coordinates(file, source_system, target_system):
    url = urljoin(BACKEND_URL, "/convert-coordinates/")
    files = {"file": (file.name, file.getvalue(), file.type)}
    data = {"source_system": source_system, "target_system": target_system}
    try:
        response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            return BytesIO(response.content)
        else:
            st.error(f"Ошибка: {response.text}")
            return None
    except Exception as e:
        st.error(f"Ошибка связи с API: {str(e)}")
        return None

def generate_markdown_report(file, source_system, target_system):
    url = urljoin(BACKEND_URL, "/generate-report/")
    files = {"file": (file.name, file.getvalue(), file.type)}
    data = {"source_system": source_system, "target_system": target_system}
    try:
        response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            return BytesIO(response.content)
        else:
            st.error(f"Ошибка: {response.text}")
            return None
    except Exception as e:
        st.error(f"Ошибка связи с API: {str(e)}")
        return None

def main():
    st.markdown("Загрузите CSV или Excel файл и преобразуйте координаты между системами.")

    uploaded_file = st.file_uploader("Выберите CSV или Excel файл", type=['csv', 'xlsx', 'xls'])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            required_columns = ["Name", "X", "Y", "Z"]
            if not all(col in df.columns for col in required_columns):
                st.error(f"Файл должен содержать колонки: {required_columns}")
                return

            uploaded_file.seek(0)

            col1, col2 = st.columns(2)
            with col1:
                source_system = st.selectbox("Исходная система", options=COORD_SYSTEMS)
            with col2:
                target_system = st.selectbox("Целевая система", options=COORD_SYSTEMS)

            if st.button("Преобразовать координаты"):
                with st.spinner("Преобразование..."):
                    converted_data = convert_coordinates(uploaded_file, source_system, target_system)
                if converted_data:
                    st.download_button(
                        label="Скачать CSV",
                        data=converted_data,
                        file_name="converted.csv",
                        mime="text/csv"
                    )

            if st.button("Сформировать Markdown-отчет"):
                with st.spinner("Формирование отчёта..."):
                    report_data = generate_markdown_report(uploaded_file, source_system, target_system)
                if report_data:
                    st.download_button(
                        label="Скачать Markdown-отчет",
                        data=report_data,
                        file_name="report.md",
                        mime="text/markdown"
                    )

        except Exception as e:
            st.error(f"Ошибка: {str(e)}")

if __name__ == "__main__":
    main()