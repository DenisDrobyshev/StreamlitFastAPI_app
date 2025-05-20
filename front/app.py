import streamlit as st
import requests
from urllib.parse import urljoin
import pandas as pd
from datetime import datetime
import base64
from io import BytesIO

BACKEND_URL = "https://streamlitfastapi-app.onrender.com"

st.set_page_config(page_title="Преобразование координат", layout="wide")
st.title("Система преобразования координат")
st.markdown("Загрузите CSV-файл со столбцами name, x, y, z для преобразования.")

COORDINATE_SYSTEMS = {
    "СК-42": "russian42",
    "ПЗ-90.11": "pz9011",
    "WGS84_G1150": "wgs84",
    "ГСК-2011": "gsk2011",
    "ITRF-2008": "itrf08",
    "СК-95": "russian95",
    "ПЗ-90": "pz90",
    "ПЗ-90.02": "pz9002"
}

def transform_data(file, source_system, target_system):
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

def main_interface():
    with st.container(border=True):
        uploaded_file = st.file_uploader(
            "Перетащите файл с координатами", 
            type=["csv", "xlsx"],
            help="Поддерживаются xlsx и csv файлы с координатами name x y z"
        )

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file) if uploaded_file.type == "text/csv" else pd.read_excel(uploaded_file)
            
            if not {"Name", "X", "Y", "Z"}.issubset(df.columns):
                st.error("Неверная структура файла")
                return

            with st.container():
                with st.subheader("Параметры преобразования"):
                    src_sys = st.selectbox(
                        "Исходная система", 
                        options=list(COORDINATE_SYSTEMS.keys()),
                        index=3
                    )
                    tgt_sys = st.selectbox(
                        "Целевая система", 
                        options=list(COORDINATE_SYSTEMS.keys()),
                        index=5
                    )
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Конвертировать", use_container_width=True):
                            with st.spinner("Преобразование..."):
                                result = transform_data(uploaded_file, src_sys, tgt_sys)
                                if result:
                                    st.session_state.converted_data = result
                    with c2:
                        if st.button("Создать отчет", type="secondary", use_container_width=True):
                            with st.spinner("Формируем отчёт..."):
                                report_data = generate_markdown_report(uploaded_file, src_sys, tgt_sys)
                            if report_data:
                                st.download_button(
                                    label="Скачать отчет в формате Markdown",
                                    data=report_data,
                                    file_name="report.md",
                                    mime="text/markdown"
                                )

            if "converted_data" in st.session_state:
                st.divider()
                st.success("Конец преобразования")
                st.download_button(
                    label="Скачать результат",
                    data=st.session_state.converted_data,
                    file_name="transformed_coordinates.csv",
                    mime="text/csv",
                    type="primary"
                )

        except Exception as e:
            st.error(f"Критическая ошибка: {str(e)}")


if __name__ == "__main__":
    main_interface()