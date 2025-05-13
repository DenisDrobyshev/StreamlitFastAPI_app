import streamlit as st
import pandas as pd
import requests
import io
import base64
from datetime import datetime

# Конфигурация
BACKEND_URL = "http://localhost:8000"  # Измените на URL вашего развернутого бэкенда

st.set_page_config(
    page_title="Система преобразования координат",
    page_icon="📍",
    layout="wide"
)

st.title("Система преобразования координат")
st.markdown("""
Это приложение позволяет преобразовывать координатные данные из Excel-файлов.
Загрузите ваш Excel-файл, содержащий координаты x, y, z, чтобы начать.
""")

# Загрузка файла
uploaded_file = st.file_uploader("Выберите Excel-файл", type=['xlsx', 'xls', 'csv'])

if uploaded_file is not None:
    try:
        # Отображение исходных данных
        df = pd.read_excel(uploaded_file)
        st.subheader("Исходные данные")
        st.dataframe(df)
        
        # Параметры преобразования
        st.subheader("Параметры преобразования")
        col1, col2 = st.columns(2)
        
        with col1:
            rotation_angle = st.slider("Угол поворота (градусы)", 0, 360, 45)
        
        with col2:
            z_offset = st.number_input("Смещение по оси Z", value=100.0)
        
        # Кнопка преобразования
        if st.button("Преобразовать координаты"):
            with st.spinner("Выполняется преобразование координат..."):
                # Подготовка файла для загрузки
                files = {'file': ('coordinates.xlsx', uploaded_file.getvalue())}
                
                try:
                    # Отправка запроса на бэкенд
                    response = requests.post(f"{BACKEND_URL}/transform", files=files)
                    response.raise_for_status()
                    
                    # Обработка ответа
                    result = response.json()
                    
                    # Отображение преобразованных данных
                    st.subheader("Преобразованные данные")
                    transformed_df = pd.DataFrame(result['transformed_data'])
                    st.dataframe(transformed_df)
                    
                    # Отображение отчета
                    st.subheader("Отчет о преобразовании")
                    st.markdown(result['markdown_report'])
                    
                    # Кнопки скачивания
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Скачивание преобразованных данных в Excel
                        transformed_excel = transformed_df.to_excel(index=False)
                        st.download_button(
                            label="Скачать преобразованные данные (Excel)",
                            data=transformed_excel,
                            file_name=f"transformed_coordinates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    
                    with col2:
                        # Скачивание отчета
                        st.download_button(
                            label="Скачать отчет (Markdown)",
                            data=result['markdown_report'],
                            file_name=f"transformation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                            mime="text/markdown"
                        )
                    
                except requests.exceptions.RequestException as e:
                    st.error(f"Ошибка подключения к серверу: {str(e)}")
                except Exception as e:
                    st.error(f"Произошла ошибка: {str(e)}")
    
    except Exception as e:
        st.error(f"Ошибка чтения Excel-файла: {str(e)}")

# Добавление подвала
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Система преобразования координат | Создано с использованием Streamlit и FastAPI</p>
</div>
""", unsafe_allow_html=True) 