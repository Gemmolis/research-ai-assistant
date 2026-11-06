import asyncio
import logging
import os
import io
import fitz
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from dotenv import load_dotenv

from core import generate_summary

load_dotenv()
logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я ИИ-ассистент для конспектирования научных статей.\n\n"
        "Вы можете отправить мне текст статьи текстом ИЛИ загрузить PDF-файл со статьей. "
        "Я выделю Введение, Методы, Результаты, Выводы и сгенерирую вопросы для самопроверки."
    )

# Обработчик текстовых сообщений
@dp.message(F.text & ~F.text.startswith('/'))
async def handle_text(message: types.Message):
    article_text = message.text
    if len(article_text) < 200:
        await message.answer("⚠️ Текст слишком короткий. Пожалуйста, отправьте полноценный текст (минимум 200 символов).")
        return
    await process_article(message, article_text)

# Обработчик PDF-файлов
@dp.message(F.document)
async def handle_document(message: types.Message):
    document = message.document
    
    # Проверяем, что это PDF
    if not document.file_name.lower().endswith('.pdf'):
        await message.answer("⚠️ Пожалуйста, загрузите файл в формате PDF.")
        return

    status_msg = await message.answer("📥 Получил PDF-файл. Извлекаю текст...")
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        # Скачиваем файл в память
        file_info = await bot.get_file(document.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        
        # Извлекаем текст из PDF с помощью PyMuPDF (fitz)
        article_text = ""
        # Открываем PDF из байтов
        doc = fitz.open(stream=downloaded_file.read(), filetype="pdf")
        for page in doc:
            article_text += page.get_text() + "\n"
        doc.close()

        # --- ДЛЯ ОТЛАДКИ (проверяем, что текст извлекся правильно) ---
        print("\n--- ПЕРВЫЕ 300 СИМВОЛОВ ИЗ PDF ---")
        print(article_text[:300])
        print("----------------------------------\n")
        
        if len(article_text.strip()) < 200:
            await status_msg.edit_text("⚠️ Не удалось извлечь достаточно текста из PDF. Возможно, это отсканированное изображение.")
            return

        await status_msg.edit_text("✅ Текст извлечен! Анализирую статью...")
        await process_article(message, article_text)

    except Exception as e:
        logging.error(f"Ошибка при чтении PDF: {e}")
        await status_msg.edit_text("❌ Ошибка при чтении PDF-файла. Попробуйте другой файл.")

# Общая функция для генерации конспекта
async def process_article(message: types.Message, article_text: str):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    status_msg = await message.answer("⏳ Готовлю конспект. Пожалуйста, подождите (10-20 сек)...")

    try:
        summary = generate_summary(article_text)
        if summary:
            if len(summary) > 4000:
                for i in range(0, len(summary), 4000):
                    await message.answer(summary[i:i+4000])
            else:
                await message.answer(summary)
            await status_msg.delete()
        else:
            await message.answer("❌ Произошла ошибка при генерации конспекта.")
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.answer("❌ Непредвиденная ошибка.")

async def main():
    print("🤖 Бот запущен с поддержкой PDF! Нажмите Ctrl+C для остановки.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())