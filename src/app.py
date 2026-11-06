import streamlit as st
import sys
import os

# Добавляем текущую директорию в путь, чтобы Streamlit видел наш core.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core import generate_summary

# Настройка страницы
st.set_page_config(page_title="AI Research Assistant", page_icon="📚", layout="wide")

# Заголовок и описание
st.title("📚 ИИ-Ассистент для конспектирования научных статей")
st.markdown("""
Этот инструмент поможет вам быстро и грамотно проанализировать научную статью. 
Вставьте текст статьи ниже, и ассистент выделит ключевые тезисы, структурирует материал и подготовит вопросы для самопроверки.
""")

# Создаем две колонки для ввода текста и вывода результата
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Исходный текст")
    article_text = st.text_area(
        "Вставьте текст научной статьи сюда:", 
        height=500,
        placeholder="Например: Настоящее исследование направлено на..."
    )
    
    # Кнопка запуска
    generate_button = st.button("🚀 Сделать конспект", type="primary", use_container_width=True)

with col2:
    st.subheader("📋 Результат")
    
    if generate_button:
        if not article_text.strip():
            st.warning("Пожалуйста, вставьте текст статьи перед генерацией.")
        else:
            with st.spinner("Анализирую текст и формирую конспект... Это может занять несколько секунд."):
                # Вызываем нашу функцию из core.py
                result = generate_summary(article_text)
                
                if result:
                    # Выводим результат в формате Markdown
                    st.markdown(result)
                    st.success("Конспект успешно сгенерирован!")
                else:
                    st.error("Произошла ошибка при генерации. Проверьте логи в терминале.")
    else:
        # Заглушка, пока кнопка не нажата
        st.info("Здесь появится ваш структурированный конспект и вопросы для самопроверки.")