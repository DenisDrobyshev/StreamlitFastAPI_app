import streamlit as st
import pandas as pd
import requests
import io
import base64
from datetime import datetime
import matplotlib.pyplot as plt
from docx import Document
from io import BytesIO


# Конфигурация
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

def display_statistics(stats: dict):
    st.subheader("Основные статистики")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Среднее X", f"{stats['mean']['x']:.2f}")
        st.metric("Медиана X", f"{stats['median']['x']:.2f}")
    
    with col2:
        st.metric("Среднее Y", f"{stats['mean']['y']:.2f}")
        st.metric("Медиана Y", f"{stats['median']['y']:.2f}")
    
    with col3:
        st.metric("Среднее Z", f"{stats['mean']['z']:.2f}")
        st.metric("Медиана Z", f"{stats['median']['z']:.2f}")
    
    st.write("")
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.metric("Мин/Макс X", f"{stats['min']['x']:.2f} / {stats['max']['x']:.2f}")
    
    with col5:
        st.metric("Мин/Макс Y", f"{stats['min']['y']:.2f} / {stats['max']['y']:.2f}")
    
    with col6:
        st.metric("Мин/Макс Z", f"{stats['min']['z']:.2f} / {stats['max']['z']:.2f}")

# Загрузка файла
uploaded_file = st.file_uploader("Выберите Excel-файл", type=['xlsx', 'xls', 'csv'])

if uploaded_file is not None:
    try:
        # Предпросмотр данных
        df = pd.read_excel(uploaded_file)
        st.subheader("Предпросмотр данных")
        st.dataframe(df.head())
        
        if st.button("Проанализировать данные"):
            with st.spinner("Анализируем данные..."):
                files = {'file': ('coordinates.xlsx', uploaded_file.getvalue())}
                
                try:
                    response = requests.post(f"{BACKEND_URL}/analyze", files=files)
                    response.raise_for_status()
                    result = response.json()
                    
                    # Отображаем статистику
                    display_statistics(result['statistics'])
                    
                    # Отображаем графики
                    st.subheader("Визуализация данных")
                    plots_bytes = base64.b64decode(result['plots_base64'])
                    st.image(plots_bytes)
                    
                    # Отчет в Markdown
                    st.subheader("Отчет в Markdown")
                    st.markdown(result['markdown_report'])
                    
                    # Кнопки скачивания
                    st.subheader("Скачать отчеты")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Word отчет
                        word_bytes = base64.b64decode(result['word_report'])
                        st.download_button(
                            label="Скачать Word отчет",
                            data=word_bytes,
                            file_name=f"coordinates_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                    
                    with col2:
                        # Markdown отчет
                        st.download_button(
                            label="Скачать Markdown отчет",
                            data=result['markdown_report'],
                            file_name=f"coordinates_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                            mime="text/markdown"
                        )
                    
                except requests.exceptions.RequestException as e:
                    st.error(f"Ошибка подключения к серверу: {str(e)}")
                except Exception as e:
                    st.error(f"Произошла ошибка: {str(e)}")
    
    except Exception as e:
        st.error(f"Ошибка чтения файла: {str(e)}")

st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Система анализа координат | Создано с использованием Streamlit и FastAPI</p>
</div>
""", unsafe_allow_html=True)