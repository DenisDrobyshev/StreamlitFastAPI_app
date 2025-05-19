import streamlit as st
import requests
import io


BACKEND_URL = "https://streamlitfastapi-app.onrender.com"

st.set_page_config(
    page_title="Анализ координатных данных",
    page_icon="📊",
    layout="wide"
)

st.title("Анализ координатных данных")
st.markdown("""
Загрузите Excel-файл с координатами x, y, z для получения статистического отчета.
""")

uploaded_file = st.file_uploader("Выберите CSV-файл", type=["csv"])

if uploaded_file is not None:
    if st.button("Преобразовать координаты"):
        with st.spinner("Обработка файла..."):
            try:
                # Отправка файла на бэкенд
                files = {"file": (uploaded_file.name, uploaded_file, "text/csv")}
                response = requests.post(f"{BACKEND_URL}/process-csv/", files=files)

                if response.status_code == 200:
                    st.download_button(
                        label="Скачать Markdown-отчет",
                        data=response.content,
                        file_name="report.md",
                        mime="text/markdown"
                    )
                    st.success("Отчет успешно сгенерирован!")
                else:
                    # Ошибка — пытаемся разобрать JSON
                    try:
                        error_detail = response.json().get('detail', 'Неизвестная ошибка')
                    except ValueError:
                        error_detail = response.text or 'Неизвестная ошибка'
                    st.error(f"Ошибка: {error_detail}")

            except requests.exceptions.RequestException as e:
                st.error(f"Ошибка подключения: {str(e)}")

st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Система анализа координат | Создано с использованием Streamlit и FastAPI</p>
</div>
""", unsafe_allow_html=True)